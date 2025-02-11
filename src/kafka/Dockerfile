FROM apache/kafka-native

USER root
RUN apk add openjdk8

WORKDIR /home/appuser
RUN wget https://dlcdn.apache.org/kafka/3.9.0/kafka_2.13-3.9.0.tgz
RUN tar -xzf kafka_2.13-3.9.0.tgz
RUN mv kafka_2.13-3.9.0 kafka
