package main

import (
	"context"
	"fmt"
	"net"
	"os"

	"github.com/exaring/otelpgx"
	"github.com/jackc/pgx/v5/pgxpool"
	log "github.com/sirupsen/logrus"

	"go.opentelemetry.io/otel/trace"
)

type TradeService struct {
	postgres *pgxpool.Pool
}

const tradesSqlTable = `
	CREATE TABLE trades(
		trade_id VARCHAR(100) PRIMARY KEY,
		customer_id VARCHAR(100) NOT NULL,
		timestamp timestamp default current_timestamp,
		symbol VARCHAR(10) NOT NULL,
		shares int NOT NULL,
		share_price float NOT NULL,
		action VARCHAR(10) NOT NULL,
		constraint shares_nonnegative check (shares >= 0),
		constraint share_price_nonnegative check (share_price >= 0)
	)
`

func NewTradeService() (*TradeService, error) {
	c := TradeService{}

	// build connection string
	url := "postgres://" + os.Getenv("POSTGRES_USER") + ":" + os.Getenv("POSTGRES_PASSWORD") + "@" + os.Getenv("POSTGRES_HOST") + ":5432/trades"
	cfg, err := pgxpool.ParseConfig(url)
	if err != nil {
		return nil, err
	}

	// connect in OTel tracer as middleware
	cfg.ConnConfig.Tracer = otelpgx.NewTracer(otelpgx.WithTrimSQLInSpanName(), otelpgx.WithDisableQuerySpanNamePrefix())
	if cfg.ConnConfig.Tracer == nil {
		return nil, fmt.Errorf("unable to create otelpgx tracer")
	}

	// build config
	conn, err := pgxpool.NewWithConfig(context.Background(), cfg)
	if err != nil {
		return nil, err
	}
	c.postgres = conn

	// try to create initial table
	_, err = conn.Exec(context.Background(), tradesSqlTable)
	if err != nil {
		// if unable to connect, die and retry
		if _, ok := err.(net.Error); ok {
			log.Fatal("unable to connect to database: ", err)
			os.Exit(1)
		} else {
			log.Warn("unable to create table: ", err)
		}
	}

	return &c, nil
}

func (c *TradeService) RecordTrade(context context.Context, trade *Trade) (*Trade, error) {

	sqlStatement := `
		INSERT INTO trades (trade_id, customer_id, symbol, action, shares, share_price)
		VALUES ($1, $2, $3, $4, $5, $6)
	`

	// insert trade
	_, err := c.postgres.Exec(context, sqlStatement, trade.TradeId, trade.CustomerId, trade.Symbol, trade.Action, trade.Shares, trade.SharePrice)
	if err != nil {
		span := trace.SpanFromContext(context)
		span.RecordError(err, trace.WithStackTrace(true))
		return nil, err
	}

	logger.WithContext(context).Info("trade committed")

	return trade, nil
}
