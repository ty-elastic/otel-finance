package main

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
)

func notify(context context.Context, trade *Trade) {
	logger.WithContext(context).Info("notifying...")

	apiUrl := "http://notifier:5000/notify"
	jsonTrade, err := json.Marshal(trade)
	if err != nil {
		logger.WithContext(context).Warnf("failure to marshall trade: %s", err)
		return
	}

	client := http.Client{}

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
