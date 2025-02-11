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
        private readonly CancellationTokenSource _cancellationTokenSource;

        private BaggagePropagator baggagePropagator;

        public KafkaConsumer(IConfiguration configuration, ILogger<KafkaConsumer> logger)
        {
            _logger = logger;

            baggagePropagator = new BaggagePropagator();

            var config = new ConsumerConfig();
            configuration.GetSection("Kafka:ConsumerSettings").Bind(config);

            _consumer = new ConsumerBuilder<int, string>(config)
                .SetValueDeserializer(Deserializers.Utf8)
                .Build();
            _topic = configuration["Kafka:Topic"];
            _cancellationTokenSource = new CancellationTokenSource();
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
                int retryCount = 0;
                const int maxRetryCount = 5;
                const int delayMilliseconds = 5000;

                while (retryCount < maxRetryCount && !_cancellationTokenSource.Token.IsCancellationRequested)
                {
                    try
                    {
                        while (!_cancellationTokenSource.Token.IsCancellationRequested)
                        {
                            try
                            {
                                _consumer.ConsumeWithInstrumentation((result) =>
                                {
                                    if (result != null) {
                                        _logger.LogInformation($"Consumed message '{result.Message.Value}' at: '{result.TopicPartitionOffset}'.");

                                        // for header in result.Message.Headers. {
                                        //     _logger.LogInformation("{hdrs}", result.Message.Headers.);
                                        // }

                                        var baggage = result.Message.Headers?.FirstOrDefault(x => x.Key == "baggage");
                                        if (baggage != null) {
                                            var val = System.Text.Encoding.UTF8.GetString(baggage.GetValueBytes());
                                            _logger.LogInformation(val);
                                        }
                                    }

                                }, 2000);
                            }
                            catch (ConsumeException e)
                            {
                                _logger.LogError($"Consume error: {e.Error.Reason}");
                            }
                        }
                    }
                    catch (KafkaException e)
                    {
                        _logger.LogError($"Kafka error: {e.Message}");
                        retryCount++;
                        _logger.LogInformation($"Retrying to connect ({retryCount}/{maxRetryCount})...");
                        Thread.Sleep(delayMilliseconds);
                    }
                }

                if (retryCount == maxRetryCount)
                {
                    _logger.LogError("Failed to connect to Kafka after maximum retry attempts.");
                }
                else
                {
                    _logger.LogInformation("Kafka consumer has stopped.");
                }
            }, _cancellationTokenSource.Token);
        }
    }
}
