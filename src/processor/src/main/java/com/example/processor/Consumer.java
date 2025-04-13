package com.example.processor;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.errors.WakeupException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.kafka.common.serialization.IntegerDeserializer;
import org.apache.kafka.common.serialization.StringDeserializer;

import java.time.Duration;
import java.util.Arrays;
import java.util.Properties;

public class Consumer {
    private static final Logger log = LoggerFactory.getLogger(Consumer.class);

    private final String topicName;

    private KafkaConsumer<Integer, String> consumer;

    public KafkaConsumer<Integer, String> createKafkaConsumer(String bootstrapServer, String groupName) {
        Properties props = new Properties();
        // bootstrap server config is required for producer to connect to brokers
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServer);
        // client id is not required, but it's good to track the source of requests beyond just ip/port
        // by allowing a logical application name to be included in server-side request logging
        //props.put(ConsumerConfig.CLIENT_ID_CONFIG, "client-" + UUID.randomUUID());

        props.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, IntegerDeserializer.class.getName());
        props.setProperty(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.setProperty(ConsumerConfig.GROUP_ID_CONFIG, groupName);
        props.setProperty(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        return new KafkaConsumer<>(props);
    }

    public Consumer(String bootstrapServer, String topicName, String groupName) {
        this.topicName = topicName;
        consumer = createKafkaConsumer(bootstrapServer, groupName);
    }

    public void wakeup() {
        consumer.wakeup();
    }

    public void run(Coordinator coordinator, Producer producer) {

        try {
            // subscribe consumer to our topic(s)
            consumer.subscribe(Arrays.asList(this.topicName));

            // poll for new data
            while (true) {
                ConsumerRecords<Integer, String> records =
                        consumer.poll(Duration.ofMillis(100));

                for (ConsumerRecord<Integer, String> record : records) {
                    log.info("Key: " + record.key() + ", Value: " + record.value());
                    log.info("Partition: " + record.partition() + ", Offset:" + record.offset());

                    if (producer != null)
                        producer.notify(record.value());
                }

                if (coordinator != null) {
                    int sleep = coordinator.getLatency();
                    Thread.sleep(sleep);
                }
            }

        } catch (WakeupException e) {
            log.info("Wake up exception!");
            // we ignore this as this is an expected exception when closing a consumer
        } catch (Exception e) {
            log.error("Unexpected exception", e);
        } finally {
            consumer.close(); // this will also commit the offsets if need be.
            log.info("The consumer is now gracefully closed.");
        }

    }
}