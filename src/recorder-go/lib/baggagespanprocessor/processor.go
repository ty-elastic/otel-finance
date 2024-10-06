package spanbaggage

import (
	"context"

	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/baggage"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

// Annotator is a SpanProcessor that adds attributes to all started spans.
type BaggageSpanProcessor struct {
	// AttrsFunc is called when a span is started. The attributes it returns
	// are set on the Span being started.
	AttrsFunc func() []attribute.KeyValue
}

func (a BaggageSpanProcessor) OnStart(context context.Context, s sdktrace.ReadWriteSpan) {
	// pull baggage from context
	traceBaggage := baggage.FromContext(context)
	for _, member := range traceBaggage.Members() {
		// set all baggage as span attributes
		s.SetAttributes(
			attribute.String(member.Key(), member.Value()),
		)
	}
}
func (a BaggageSpanProcessor) Shutdown(context.Context) error   { return nil }
func (a BaggageSpanProcessor) ForceFlush(context.Context) error { return nil }
func (a BaggageSpanProcessor) OnEnd(s sdktrace.ReadOnlySpan)    {}
