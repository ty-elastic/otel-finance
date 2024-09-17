# Non-Instruqt

If operating outside of Instruqt (on your own laptop, to your own Elasticsearch cluster), you will need to provide appropriate credentials. Create a `.env` file in this directory with the following variables define:

```
ELASTIC_APM_SERVER_ENDPOINT=
ELASTIC_APM_SERVER_SECRET=
ELASTIC_APM_SERVER_RUM_ENDPOINT=
ELASTIC_APM_SERVER_RUM_CREDENTIALS=false
```

And then load the variables
```export source .env```

# Building

1. Open a Terminal in VS Code (drag divider from bottom)
2. `cd` to `/workspace`
3. `docker-compose build`

# Running

1. `docker-compose up`

# Playing around

* use the "Record Store" Instruqt tab (or `http://127.0.0.1:9394` if running locally) to interact with the UI
* use the "Elastic - APM" tab (or visit your Elastic cluster) to interact with Elastic APM

# Architecture

![arch](docs/arch.jpg)

# Data Collection

This demo also shows how to obtain record count and data sizes of APM traffic flowing through a collector in order to help size an Elasticsearch cluster.

```mermaid
flowchart TB
    subgraph Service1[MyService]
    func[function]
    OTEL1[OTel APM Agent]
    func == "span()" ==> OTEL1
    end
    OTEL1[OTel Instrumentation Lib] == span/OTLP ==> EdgeCollector
    EdgeCollector == span/OTLP ==> APMBackend
    subgraph DebugCollector
    subgraph Service
    TraceReceiver ==> FilterProcessor[filter for service.name==MyService]
    FilterProcessor ==> LoggingBasic
    end
    Service == metrics ==> PrometheusEndpoint
    subgraph Telemetry
    PrometheusScraperReceiver ==> FilterProcessor2[filter for count and size metrics]
    FilterProcessor2 ==> LoggingDetails
    end
    PrometheusEndpoint ==> PrometheusScraperReceiver
    end
    EdgeCollector == span/OTLP ==> TraceReceiver

```