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
	response, error := client.Do(req)
	if error != nil {
		fmt.Println(error)
	}
	fmt.Println("Status: ", response.Status)
}
