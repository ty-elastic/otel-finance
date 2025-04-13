FROM maven:3-eclipse-temurin-17 AS build  
COPY src /usr/src/app/src  
COPY pom.xml /usr/src/app
WORKDIR /usr/src/app
RUN mvn package -Dmaven.test.skip

FROM eclipse-temurin:17

COPY --from=build /usr/src/app/target/processor-0.0.1-SNAPSHOT.jar /processor.jar

RUN wget -O elastic-otel-javaagent.jar https://repo1.maven.org/maven2/co/elastic/otel/elastic-otel-javaagent/1.2.1/elastic-otel-javaagent-1.2.1.jar 

ENV COORDINATOR_HOST=""

ENV BOOTSTRAP_SERVER=""
ENV IN_TOPIC=""
ENV IN_GROUP=""
ENV OUT_TOPIC=""
ENV PRODUCER_SLEEP_MS=""

EXPOSE 9003
ENTRYPOINT java \
-javaagent:elastic-otel-javaagent.jar \
-Dotel.java.experimental.span-attributes.copy-from-baggage.include=* \
-Dotel.java.experimental.span-stacktrace.min.duration=-1 \
-jar /processor.jar \
--coordinator_host=${COORDINATOR_HOST} \
--bootstrap_server=${BOOTSTRAP_SERVER} \
--producer_sleep_ms=${PRODUCER_SLEEP_MS} \
--in_topic=${IN_TOPIC} \
--in_group=${IN_GROUP} \
--out_topic=${OUT_TOPIC}
