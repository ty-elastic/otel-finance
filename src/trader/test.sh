export POSTGRES_HOST=127.0.0.1
export POSTGRES_USER=admin
export POSTGRES_PASSWORD=password

export OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4317"
export OTEL_RESOURCE_ATTRIBUTES="service.version=1.0"

OTEL_SERVICE_NAME="trader" opentelemetry-instrument flask run --host=0.0.0.0 -p 9000
