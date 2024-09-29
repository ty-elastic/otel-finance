FROM maven:3-eclipse-temurin-17 AS build  
COPY src /usr/src/app/src  
COPY pom.xml /usr/src/app
WORKDIR /usr/src/app
RUN mvn package -Dmaven.test.skip

FROM eclipse-temurin:17

COPY --from=build /usr/src/app/target/recorder-0.0.1-SNAPSHOT.jar /recorder-0.0.1-SNAPSHOT.jar
COPY elastic-otel-javaagent-1.0.0.jar /elastic-otel-javaagent-1.0.0.jar
COPY opentelemetry-java-baggage-log-record-processor-1.0-all.jar /opentelemetry-java-baggage-log-record-processor-1.0-all.jar

ENTRYPOINT ["java", "-javaagent:elastic-otel-javaagent-1.0.0.jar", "-Dotel.javaagent.extensions=opentelemetry-java-baggage-log-record-processor-1.0-all.jar", "-Dotel.java.experimental.span-attributes.copy-from-baggage.include=*", "-jar", "/recorder-0.0.1-SNAPSHOT.jar"]
