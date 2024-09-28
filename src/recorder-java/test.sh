export POSTGRES_HOST=127.0.0.1
export POSTGRES_USER=admin
export POSTGRES_PASSWORD=password

export OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4318"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
export OTEL_SERVICE_NAME="recorder-java"

cd ../lib/java/baggage-log-record-processor
./gradlew build
cd ../../../recorder-java
cp ../lib/java/baggage-log-record-processor/build/libs/opentelemetry-java-baggage-log-record-processor-1.0-all.jar .

mvn package -Dmaven.test.skip
java -javaagent:elastic-otel-javaagent-1.0.0.jar -Dotel.javaagent.extensions=opentelemetry-java-instrumentation-extension-demo-1.0-all.jar -Dotel.java.experimental.span-attributes.copy-from-baggage.include=* -jar target/recorder-0.0.1-SNAPSHOT.jar
