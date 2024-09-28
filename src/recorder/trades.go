package main

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"os"
	"strconv"

	"github.com/exaring/otelpgx"
	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5/pgxpool"
	log "github.com/sirupsen/logrus"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/baggage"
	"go.opentelemetry.io/otel/trace"
)

const albumsSqlTable = `
	CREATE TABLE trades(
		trade_id VARCHAR(100) PRIMARY KEY,
		customer_id VARCHAR(100) NOT NULL,
		timestamp timestamp default current_timestamp,
		symbol VARCHAR(10) NOT NULL,
		shares int NOT NULL,
		share_price float NOT NULL,
		action VARCHAR(10) NOT NULL
	)
`

func (c *Recorder) initPostgres() error {
	// build connection string
	url := "postgres://" + os.Getenv("POSTGRES_USER") + ":" + os.Getenv("POSTGRES_PASSWORD") + "@" + os.Getenv("POSTGRES_HOST") + ":5432/trades"
	cfg, err := pgxpool.ParseConfig(url)
	if err != nil {
		return err
	}

	// connect in OTel tracer as middleware
	cfg.ConnConfig.Tracer = otelpgx.NewTracer()
	if cfg.ConnConfig.Tracer == nil {
		return fmt.Errorf("unable to create otelpgx tracer")
	}

	// build config
	conn, err := pgxpool.NewWithConfig(context.Background(), cfg)
	if err != nil {
		return err
	}
	c.postgres = conn

	// try to create initial table
	_, err = conn.Exec(context.Background(), albumsSqlTable)
	if err != nil {
		// if unable to connect, die and retry
		if _, ok := err.(net.Error); ok {
			log.Fatal("unable to connect to database: ", err)
			os.Exit(1)
		} else {
			log.Warn("unable to create table: ", err)
		}
	}

	return nil
}

func (c *Recorder) recordTrade(ctx *gin.Context) {
	customerId := ctx.Query("customer_id")
	tradeId := ctx.Query("trade_id")
	symbol := ctx.Query("symbol")
	shares, _ := strconv.ParseInt(ctx.Query("shares"), 10, 32)
	sharePrice, _ := strconv.ParseFloat(ctx.Query("share_price"), 32)
	action := ctx.Query("action")

	// get current span context (from auto-instrumentation)
	span := trace.SpanFromContext(ctx.Request.Context())

	// pull baggage from context (gin otel middleware pulled it from request headers and put it onto context for us)
	traceBaggage := baggage.FromContext(ctx.Request.Context())
	for _, member := range traceBaggage.Members() {
		// set all baggage as span attributes
		span.SetAttributes(
			attribute.String(member.Key(), member.Value()),
		)
	}

	sqlStatement := `
		INSERT INTO trades (trade_id, customer_id, symbol, action, shares, share_price)
		VALUES ($1, $2, $3, $4, $5, $6)
	`

	// insert trade
	returnval, err := c.postgres.Exec(ctx, sqlStatement, tradeId, customerId, symbol, action, shares, sharePrice)
	fmt.Printf("value of returnval %s", returnval)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, err.Error())
		return
	}

	logger.WithContext(ctx.Request.Context()).Info("trade committed")

	ctx.JSON(http.StatusOK, gin.H{
		"trade_id": tradeId,
		"result":   "committed",
	})
}
