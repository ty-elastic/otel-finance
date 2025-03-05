using Confluent.Kafka;
using System.Diagnostics;
using System.Diagnostics.Metrics;

namespace KafkaApi.Services
{
    public class KafkaConsumer : BackgroundService
    {
        private readonly IConsumer<int, string> _consumer;
        private readonly string _topic;
        private readonly ILogger<KafkaConsumer> _logger;

        private readonly ActivitySource _activitySource;

        private readonly Counter<long> _successCounter;

        public KafkaConsumer(IConfiguration configuration, ILogger<KafkaConsumer> logger, InstrumentedConsumerBuilder<int, string> consumeBuilder)
        {
            _logger = logger;
            _consumer = consumeBuilder.Build();
            _topic = configuration["Kafka:Topic"];

            // .NET Diagnostics: create the span factory
            _activitySource = new ActivitySource("Notifier");

            // .NET Diagnostics: create a metric
            using var meter = new Meter("Notifier", "1.0");
            _successCounter = meter.CreateCounter<long>("notifications.kafka", description: "Number of notifications via kafka");
        }


        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _consumer.Subscribe(_topic);
            _logger.LogInformation($"Subscribed to topic: {_topic}");

            await BackgroundProcessing(stoppingToken);
        }

        private async Task BackgroundProcessing(CancellationToken stoppingToken)
        {
            await Task.Run(() => 
            {
                try
                {
                    while (true)
                    {
                        try
                        {
                            var consumeResult = _consumer.ConsumeAndProcessMessageAsync((consumeResult, activity, cancellationToken) =>  {

                                if (consumeResult.IsPartitionEOF)
                                {
                                    _logger.LogWarning(
                                        $"Reached end of topic {consumeResult.Topic}, partition {consumeResult.Partition}, offset {consumeResult.Offset}.");

                                    return new ValueTask();
                                }

                                activity?.SetTag("parent", "blah");

                                _logger.LogInformation($"Received message at {consumeResult.TopicPartitionOffset}: {consumeResult.Message.Value}");
     
                                using (var childActivity = _activitySource.StartActivity("NotifyKafka", ActivityKind.Internal, activity.Context))
                                {
                                    childActivity?.SetTag("foo", 1);
                                    childActivity?.SetTag("bar", "Hello, World!");
                                    childActivity?.SetTag("baz", new int[] { 1, 2, 3 });

                                    childActivity?.SetStatus(ActivityStatusCode.Ok);

                                    // .NET Diagnostics: update the metric
                                    _successCounter.Add(1);
                                }

                                return new ValueTask();
                            });

                            
                        }
                        catch (ConsumeException e)
                        {
                            _logger.LogWarning($"Consume error: {e.Error.Reason}");
                        }

                        
                    }
                }
                catch (OperationCanceledException)
                {
                    _logger.LogWarning("Closing consumer.");
                    _consumer.Close();
                }

            }, stoppingToken);
        }
    }
}
