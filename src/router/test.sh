export OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4318"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
export OTEL_SERVICE_NAME=router

export RECORDER_HOST_CANARY=127.0.0.1
export RECORDER_HOST=127.0.0.1

npx ts-node -r @elastic/opentelemetry-node app.ts