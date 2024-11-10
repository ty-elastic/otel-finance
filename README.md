# Running Self-Managed

While this workshop has been designed to work inside on the Instruqt execution environment, it is equally well suited to run locally against an Elastic Cloud or Serverless cluster.

## Requirements

### Execution
* working, modern docker compose stack

### Elasticsearch
* >=8.15.3
* Set `server.maxPayload` to `2048000` to allow uploads of frontend source maps

## Setup

Ensure the following ENV variables are set on the machine you will be running the demo prior to executing `docker compose build`:

| Variable Name | Description |
| ------------- | ----------- |
| KIBANA_URL    | URL (including https://...) of your Kibana server |
| ELASTICSEARCH_URL | URL (including https://...) of your Elasticsearch server |
| ELASTICSEARCH_USER | admin user for Elasticsearch cluster (e.g., `elastic`) |
| ELASTICSEARCH_PASSWORD | password for the `ELASTICSEARCH_USER` |
| ELASTICSEARCH_APIKEY | an API key created under the `ELASTICSEARCH_USER` |
| ELASTIC_APM_SERVER_ENDPOINT | URL (including https://...ending with the port :443) of your APM server |
| ELASTIC_APM_SERVER_RUM_ENDPOINT | URL (including https://...ending with the port :443) of your APM server |
| ELASTIC_APM_SERVER_SECRET | secret token to send in APM data |

Then, at the top-level directory of this repo, executing `docker compose build` to build the demo stack.

## Running

`docker compose up`

The `front-end` app will be available locally at `http://127.0.0.1:9394`.

# TO-DO

## .net
* develop an extension to set baggage on log records
* develop a PLUGIN to autoload baggageSpanProcessor and baggageLogProcessor w/o code changes

## node.js
* develop an extension to set baggage on log records
* develop a PLUGIN to autoload baggageSpanProcessor and baggageLogProcessor w/o code changes

## java
* integrate universal profiling

## workshop
* use changepoint detection for market conditions change