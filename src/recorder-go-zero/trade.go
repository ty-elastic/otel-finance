package main

type Trade struct {
	CustomerId string  `json:"customer_id"`
	TradeId    string  `json:"trade_id"`
	Symbol     string  `json:"symbol"`
	Shares     int64   `json:"shares"`
	SharePrice float64 `json:"sharePrice"`
	Action     string  `json:"action"`
}
