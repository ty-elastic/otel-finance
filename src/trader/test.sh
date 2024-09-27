export POSTGRES_HOST=127.0.0.1
export POSTGRES_USER=admin
export POSTGRES_PASSWORD=password

export OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4317"
export OTEL_RESOURCE_ATTRIBUTES="service.version=1.0"
export ELASTIC_OTEL_SYSTEM_METRICS_ENABLED=true
export OTEL_METRIC_EXPORT_INTERVAL=5000

# export OTEL_PYTHON_LOG_LEVEL="info"
# export OTEL_PYTHON_LOG_CORRELATION="true"
# export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED="true"

# pip install -r requirements.txt
#opentelemetry-bootstrap -a install

OTEL_SERVICE_NAME="trader" opentelemetry-instrument flask run --host=0.0.0.0 -p 9000
