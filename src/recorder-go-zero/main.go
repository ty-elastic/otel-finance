package main

import (
	"flag"
	"os"
	"sync"

	log "github.com/sirupsen/logrus"
)

var (
	logger            *log.Logger
	initResourcesOnce sync.Once
)

func initLogrus(logfile *string) {
	logger = log.New()

	logger.SetFormatter(&log.JSONFormatter{FieldMap: log.FieldMap{
		"msg":  "message",
		"time": "timestamp",
	}})

	if logfile != nil {
		f, err := os.OpenFile(*logfile, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0755)
		if err != nil {
			log.Fatalf("unable to open log file: %s", *logfile)
		}
		logger.SetOutput(f)
	} else {
		logger.SetOutput(os.Stdout)
	}

	logger.SetLevel(log.InfoLevel)
}

func main() {

	logfileOption := flag.String("logfile", "", "logfile path")
	flag.Parse()

	initLogrus(logfileOption)

	tradeService, _ := NewTradeService()
	tradeController, _ := NewTradeController(tradeService)

	tradeController.Run()
}
