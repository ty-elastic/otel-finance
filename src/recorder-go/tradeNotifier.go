package main

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

func notify(context context.Context, trade *Trade) {
	logger.WithContext(context).Info("notifying...")

	jsonTrade, err := json.Marshal(trade)
	if err != nil {
		logger.WithContext(context).Warnf("failure to marshall trade: %s", err)
		return
	}

	client := http.Client{Transport: otelhttp.NewTransport(http.DefaultTransport)}

	apiUrl := "http://notifier:5000/notify"
	req, err := http.NewRequestWithContext(context, "POST", apiUrl, bytes.NewReader(jsonTrade))
	if err != nil {
		logger.WithContext(context).Warnf("failure to create http req: %s", err)
		return
	}

	res, err := client.Do(req)
	defer res.Body.Close()

	if err != nil {
		logger.WithContext(context).Warnf("notification error: %s", err)
	}
}
