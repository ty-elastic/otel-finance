package main

import (
	"context"
	"flag"
	"os"
	"sync"

	log "github.com/sirupsen/logrus"

	"go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/baggage"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	sdkresource "go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/trace"

	"github.com/gin-gonic/gin"

	"github.com/jackc/pgx/v5/pgxpool"

	spanbaggage "github.com/ty-elastic/opentelemetryprocessorspanbaggage"
)

var (
	logger            *log.Logger
	resource          *sdkresource.Resource
	initResourcesOnce sync.Once
)

type Recorder struct {
	postgres *pgxpool.Pool
	gin      *gin.Engine
	tracer   trace.Tracer
}

type customLogger struct {
	formatter log.JSONFormatter
}

func (l customLogger) Format(entry *log.Entry) ([]byte, error) {
	span := trace.SpanFromContext(entry.Context)
	if span != nil {
		entry.Data["trace_id"] = span.SpanContext().TraceID().String()
		entry.Data["span_id"] = span.SpanContext().SpanID().String()
		entry.Data["service_name"] = os.Getenv("OTEL_SERVICE_NAME")

		traceBaggage := baggage.FromContext(entry.Context)
		for _, member := range traceBaggage.Members() {
			entry.Data[member.Key()] = member.Value()
		}
	}

	return l.formatter.Format(entry)
}

func initLogrus(logfile *string) {
	logger = log.New()

	logger.SetFormatter(customLogger{
		formatter: log.JSONFormatter{FieldMap: log.FieldMap{
			"msg":  "message",
			"time": "timestamp",
		}},
	})
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

func initResource() *sdkresource.Resource {
	initResourcesOnce.Do(func() {
		extraResources, _ := sdkresource.New(
			context.Background(),
			sdkresource.WithOS(),
			sdkresource.WithProcess(),
			sdkresource.WithContainer(),
			sdkresource.WithHost(),
		)
		resource, _ = sdkresource.Merge(
			sdkresource.Default(),
			extraResources,
		)
	})
	return resource
}

func initTracerProvider() *sdktrace.TracerProvider {
	ctx := context.Background()

	exporter, err := otlptracegrpc.New(ctx)
	if err != nil {
		log.Fatalf("OTLP Trace gRPC Creation: %v", err)
	}

	bsp := spanbaggage.BaggageSpanProcessor{}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(initResource()),
		sdktrace.WithSpanProcessor(bsp),
	)

	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))
	return tp
}

func (c *Recorder) initGin() error {
	r := gin.Default()
	r.Use(otelgin.Middleware(os.Getenv("OTEL_SERVICE_NAME")))

	r.POST("/trade", c.recordTrade)

	c.gin = r
	return nil
}

func main() {

	logfileOption := flag.String("logfile", "", "logfile path")
	flag.Parse()

	initLogrus(logfileOption)

	tp := initTracerProvider()
	defer func() {
		if err := tp.Shutdown(context.Background()); err != nil {
			log.Fatalf("Tracer Provider Shutdown: %v", err)
		}
	}()

	c := Recorder{
		tracer: tp.Tracer("recorder"),
	}

	c.initPostgres()

	c.initGin()
	c.gin.Run("0.0.0.0:9000")
}
