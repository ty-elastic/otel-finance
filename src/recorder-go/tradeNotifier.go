package main

import (
	"context"
	"fmt"
	"net/http"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

func notify(context context.Context, trade *Trade) {
	fmt.Println("Notifying...")

	apiUrl := "http://notifier:5000/"

	client := http.Client{Transport: otelhttp.NewTransport(http.DefaultTransport)}

	req, _ := http.NewRequestWithContext(context, "GET", apiUrl, nil)
	res, error := client.Do(req)
	if error != nil {
		fmt.Println(error)
		return
	}
	//_, _ = io.ReadAll(res.Body)
	_ = res.Body.Close()

	fmt.Println("Status: ", res.Status)
}
