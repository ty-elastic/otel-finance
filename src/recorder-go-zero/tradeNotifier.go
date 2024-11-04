package main

import (
	"context"
	"fmt"
	"net/http"
)

func notify(context context.Context, trade *Trade) {
	fmt.Println("Notifying...")

	apiUrl := "http://notifier:5000/"

	client := http.Client{}

	req, _ := http.NewRequestWithContext(context, "GET", apiUrl, nil)
	res, error := client.Do(req)
	if error != nil {
		fmt.Println(error)
		return
	}
	_ = res.Body.Close()

	fmt.Println("Status: ", res.Status)
}
