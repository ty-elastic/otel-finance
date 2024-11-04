// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

using System.Diagnostics;
using System.Diagnostics.Metrics;

// .NET Diagnostics: create the span factory
using var activitySource = new ActivitySource("Examples.Service");

// .NET Diagnostics: create a metric
using var meter = new Meter("Examples.Service", "1.0");
var successCounter = meter.CreateCounter<long>("srv.successes.count", description: "Number of successful responses");

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapPost("/notify", NotifyHandler);
app.Run();

async Task<string> NotifyHandler(ILogger<Program> logger)
{

    // .NET Diagnostics: create a manual span
    using (var activity = activitySource.StartActivity("Notify"))
    {
        activity?.SetTag("foo", 1);
        activity?.SetTag("bar", "Hello, World!");
        activity?.SetTag("baz", new int[] { 1, 2, 3 });

        activity?.SetStatus(ActivityStatusCode.Ok);

        // .NET Diagnostics: update the metric
        successCounter.Add(1);
    }

    // .NET ILogger: create a log
    logger.LogInformation("Success! Today is: {Date:MMMM dd, yyyy}", DateTimeOffset.UtcNow);

    return "Notified";
}
