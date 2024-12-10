package main

import (
	"context"
	"flag"
	"os"
	"sync"
	"time"

	log "github.com/sirupsen/logrus"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/baggage"
	"go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/metric"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/metric/metricdata"
	sdkresource "go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/trace"

	spanbaggage "github.com/ty-elastic/opentelemetryprocessorspanbaggage"
)

var (
	logger            *log.Logger
	resource          *sdkresource.Resource
	initResourcesOnce sync.Once
)

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

func newTracerProvider() *sdktrace.TracerProvider {
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

func deltaSelector(kind metric.InstrumentKind) metricdata.Temporality {
	switch kind {
	case metric.InstrumentKindCounter,
		metric.InstrumentKindGauge,
		metric.InstrumentKindHistogram,
		metric.InstrumentKindObservableGauge,
		metric.InstrumentKindObservableCounter:
		return metricdata.DeltaTemporality
	case metric.InstrumentKindUpDownCounter,
		metric.InstrumentKindObservableUpDownCounter:
		return metricdata.CumulativeTemporality
	}
	panic("unknown instrument kind")
}

func newMeterProvider() *sdkmetric.MeterProvider {
	ctx := context.Background()

	exporter, err := otlpmetricgrpc.New(ctx, otlpmetricgrpc.WithTemporalitySelector(deltaSelector))
	if err != nil {
		log.Fatalf("OTLP Trace gRPC Creation: %v", err)
	}

	mp := sdkmetric.NewMeterProvider(
		sdkmetric.WithResource(initResource()),
		sdkmetric.WithReader(sdkmetric.NewPeriodicReader(exporter,
			// Default is 1m. Set to 3s for demonstrative purposes.
			sdkmetric.WithInterval(3*time.Second))),
	)

	otel.SetMeterProvider(mp)
	return mp
}

func main() {
	logfileOption := flag.String("logfile", "", "logfile path")
	flag.Parse()

	initLogrus(logfileOption)

	tp := newTracerProvider()
	defer func() {
		if err := tp.Shutdown(context.Background()); err != nil {
			log.Fatalf("Tracer Provider Shutdown: %v", err)
		}
	}()

	mp := newMeterProvider()
	defer func() {
		if err := mp.Shutdown(context.Background()); err != nil {
			log.Fatalf("Tracer Provider Shutdown: %v", err)
		}
	}()

	tradeService, _ := NewTradeService()
	tradeController, _ := NewTradeController(tradeService)

	tradeController.Run()
}
