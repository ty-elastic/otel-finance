export POSTGRES_HOST=127.0.0.1
export POSTGRES_USER=admin
export POSTGRES_PASSWORD=password

export OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4317"
export OTEL_SERVICE_NAME="recorder-go"

cd ../../lib
./build.sh
cd ../src/recorder-go

go build -o build/recorder
build/recorder -logfile=../../logs/recorder.log
