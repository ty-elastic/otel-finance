FROM maven:3-eclipse-temurin-17 AS build  
COPY src /usr/src/app/src  
COPY pom.xml /usr/src/app
WORKDIR /usr/src/app
RUN mvn package -Dmaven.test.skip

FROM eclipse-temurin:17

COPY --from=build /usr/src/app/target/processor1-0.0.1-SNAPSHOT.jar /processor1.jar

COPY lib/ .
RUN wget -O elastic-otel-javaagent.jar https://repo1.maven.org/maven2/co/elastic/otel/elastic-otel-javaagent/1.2.1/elastic-otel-javaagent-1.2.1.jar 

ENV OTEL_SERVICE_NAME="processor1"
ENV OTEL_EXPERIMENTAL_RESOURCE_DETECTORS="process_runtime"

EXPOSE 9003
ENTRYPOINT ["java", \
"-javaagent:elastic-otel-javaagent.jar", \
"-Dotel.java.experimental.span-attributes.copy-from-baggage.include=*", \
"-Dotel.javaagent.extensions=opentelemetry-java-baggage-log-record-processor-all.jar", \
"-Dotel.java.experimental.span-stacktrace.min.duration=-1", \
"-Dotel.inferred.spans.enabled=true", "-Dotel.inferred.spans.sampling.interval=1ms", "-Dotel.inferred.spans.min.duration=0ms", "-Dotel.inferred.spans.included.classes=com.example.*", \
"-jar", "/processor1.jar"]
