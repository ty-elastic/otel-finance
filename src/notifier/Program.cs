// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

using KafkaApi.Services;
using OpenTelemetry.Resources;
using Confluent.Kafka;
using OpenTelemetry.Metrics;
using OpenTelemetry.Trace;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddLogging();

builder.Services.AddSingleton(_ =>
{
    var config = new ConsumerConfig();
    builder.Configuration.GetSection("Kafka:ConsumerSettings").Bind(config);
    return new InstrumentedConsumerBuilder<int, string>(config);
});

builder.Services.AddOpenTelemetry()
    .WithTracing(tracing =>
    {
        tracing
            .SetResourceBuilder(ResourceBuilder.CreateDefault())
            .AddProcessor(new BaggageSpanProcessor.BaggageSpanProcessor())
            .AddAspNetCoreInstrumentation()
            .AddKafkaConsumerInstrumentation<int, string>()
            .AddOtlpExporter();
    })
    .WithMetrics(metering =>
    {
        metering
            .AddOtlpExporter()
            .AddKafkaConsumerInstrumentation<int, string>();
    });

builder.Services.AddHostedService<KafkaConsumer>();

var app = builder.Build();


string HealthHandler(ILogger<Program> logger)
{
    return "KERNEL OK";
}

string NotifyHandler(ILogger<Program> logger)
{
    logger.LogInformation("notified");

    return "Notified";
}

app.MapGet("/health", HealthHandler);
app.MapPost("/notify", NotifyHandler);
await app.RunAsync();