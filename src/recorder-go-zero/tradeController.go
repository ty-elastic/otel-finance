package main

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type TradeController struct {
	gin          *gin.Engine
	tradeService *TradeService
}

func NewTradeController(tradeService *TradeService) (*TradeController, error) {
	c := TradeController{tradeService: tradeService}
	c.gin = gin.Default()

	c.gin.POST("/record", c.record)
	c.gin.GET("/health", c.health)

	return &c, nil
}

func (c *TradeController) health(ctx *gin.Context) {
	ctx.JSON(http.StatusOK, gin.H{"message": "KERNEL OK"})
}

func (c *TradeController) record(ctx *gin.Context) {
	customerId := ctx.Query("customer_id")
	tradeId := ctx.Query("trade_id")
	symbol := ctx.Query("symbol")
	shares, _ := strconv.ParseInt(ctx.Query("shares"), 10, 32)
	sharePrice, _ := strconv.ParseFloat(ctx.Query("share_price"), 32)
	action := ctx.Query("action")

	trade := Trade{CustomerId: customerId, TradeId: tradeId, Symbol: symbol, Shares: shares, SharePrice: sharePrice, Action: action}

	res, err := c.tradeService.RecordTrade(ctx.Request.Context(), &trade)

	notify(ctx.Request.Context(), &trade)

	if err != nil {
		ctx.JSON(http.StatusInternalServerError, err.Error())
	} else {
		ctx.JSON(http.StatusOK, res)
	}
}

func (c *TradeController) Run() {
	c.gin.Run("0.0.0.0:9003")
}
