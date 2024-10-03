FROM maven:3-eclipse-temurin-17 AS build  
COPY src /usr/src/app/src  
COPY pom.xml /usr/src/app
WORKDIR /usr/src/app
RUN mvn package -Dmaven.test.skip

FROM eclipse-temurin:17

COPY --from=build /usr/src/app/target/recorder-0.0.1-SNAPSHOT.jar /recorder.jar

COPY _lib/ .

EXPOSE 9003
ENTRYPOINT ["java", "-javaagent:elastic-otel-javaagent.jar", "-Dotel.inferred.spans.enabled=true", "-Dotel.inferred.spans.sampling.interval=1ms", "-Dotel.inferred.spans.min.duration=0ms", "-Dotel.inferred.spans.included.classes=com.example.*", "-Dotel.javaagent.extensions=opentelemetry-java-baggage-log-record-processor-all.jar", "-Dotel.java.experimental.span-attributes.copy-from-baggage.include=*", "-jar", "/recorder.jar"]
