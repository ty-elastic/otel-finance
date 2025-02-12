// Copyright 2020 Confluent Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// Refer to LICENSE for more information.

using System;
using System.Threading;
using System.Threading.Tasks;
using Confluent.Kafka;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using Confluent.Kafka.Extensions.Diagnostics;
using OpenTelemetry.Context.Propagation;

namespace KafkaApi.Services
{
    public class KafkaConsumer : BackgroundService
    {
        private readonly IConsumer<int, string> _consumer;
        private readonly string _topic;
        private readonly ILogger<KafkaConsumer> _logger;

        public KafkaConsumer(IConfiguration configuration, ILogger<KafkaConsumer> logger, InstrumentedConsumerBuilder<int, string> consumeBuilder)
        {
            _logger = logger;

            _consumer = consumeBuilder.Build();

            _topic = configuration["Kafka:Topic"];
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
                            var consumeResult = _consumer.Consume(stoppingToken);

                            if (consumeResult.IsPartitionEOF)
                            {
                                Console.WriteLine(
                                    $"Reached end of topic {consumeResult.Topic}, partition {consumeResult.Partition}, offset {consumeResult.Offset}.");

                                continue;
                            }

                            Console.WriteLine($"Received message at {consumeResult.TopicPartitionOffset}: {consumeResult.Message.Value}");
                        }
                        catch (ConsumeException e)
                        {
                            Console.WriteLine($"Consume error: {e.Error.Reason}");
                        }
                    }
                }
                catch (OperationCanceledException)
                {
                    Console.WriteLine("Closing consumer.");
                    _consumer.Close();
                }

            }, stoppingToken);
        }
    }
}
