// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

using KafkaApi.Services;
// using Microsoft.Extensions.DependencyInjection;
// using OpenTelemetry.Trace;
using OpenTelemetry.Resources;
// using OpenTelemetry.Exporter;
// using Confluent.Kafka.Extensions.OpenTelemetry;

// // .NET Diagnostics: create the span factory
// using var activitySource = new ActivitySource("Notifier");

// // .NET Diagnostics: create a metric
// using var meter = new Meter("Notifier", "1.0");
// var successCounter = meter.CreateCounter<long>("srv.successes.count", description: "Number of successful responses");

// var builder = WebApplication.CreateBuilder(args);

// // Add services to the container.
// builder.Services.AddHostedService<KafkaConsumer>();   
// builder.Services.AddLogging();

// builder.Services.AddOpenTelemetry()
//     .WithTracing(traceBuilder =>
//     {
//         traceBuilder
//             .SetResourceBuilder(ResourceBuilder.CreateDefault())
//             .AddProcessor(new BaggageSpanProcessor.BaggageSpanProcessor())
//             .AddAspNetCoreInstrumentation()
//             .AddConfluentKafkaInstrumentation()
//             //.AddConsoleExporter()
//             .AddOtlpExporter();
//     });

// var app = builder.Build();

// app.MapGet("/health", HealthHandler);
// app.MapPost("/notify", NotifyHandler);
// app.Run();

// string HealthHandler(ILogger<Program> logger)
// {
//     return "KERNEL OK";
// }

// string NotifyHandler(ILogger<Program> logger)
// {
//     // // .NET Diagnostics: create a manual span
//     // using (var activity = activitySource.StartActivity("Notify"))
//     // {
//     //     activity?.SetTag("foo", 1);
//     //     activity?.SetTag("bar", "Hello, World!");
//     //     activity?.SetTag("baz", new int[] { 1, 2, 3 });

//     //     activity?.SetStatus(ActivityStatusCode.Ok);

//     //     // .NET Diagnostics: update the metric
//     //     successCounter.Add(1);
//     // }

//     // .NET ILogger: create a log
//     logger.LogInformation("notified");

//     return "Notified";
// }


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
        tracing.AddConsoleExporter()
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
    // // .NET Diagnostics: create a manual span
    // using (var activity = activitySource.StartActivity("Notify"))
    // {
    //     activity?.SetTag("foo", 1);
    //     activity?.SetTag("bar", "Hello, World!");
    //     activity?.SetTag("baz", new int[] { 1, 2, 3 });

    //     activity?.SetStatus(ActivityStatusCode.Ok);

    //     // .NET Diagnostics: update the metric
    //     successCounter.Add(1);
    // }

    // .NET ILogger: create a log
    logger.LogInformation("notified");

    return "Notified";
}

app.MapGet("/health", HealthHandler);
app.MapPost("/notify", NotifyHandler);
await app.RunAsync();