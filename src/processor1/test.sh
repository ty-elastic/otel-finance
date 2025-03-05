export POSTGRES_HOST=127.0.0.1
export POSTGRES_USER=admin
export POSTGRES_PASSWORD=password

export OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4318"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
export OTEL_SERVICE_NAME="recorder-java"

cd ../../lib
./build.sh
cd ../src/recorder-java

mvn package -Dmaven.test.skip
java -javaagent:_lib/elastic-otel-javaagent.jar -Dotel.javaagent.extensions=_lib/opentelemetry-java-baggage-log-record-processor-all.jar -Dotel.java.experimental.span-attributes.copy-from-baggage.include=* -jar target/recorder-0.0.1-SNAPSHOT.jar
