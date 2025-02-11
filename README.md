## Environment Variables Setup

Create a `.env` and follow the steps below to add the necessary values:

1. while your deployment is being setup copy the `username` and `password` provided:

ELASTICSEARCH_USER=
ELASTICSEARCH_PASSWORD=

2. from `https://cloud.elastic.co/deployments` click on a deployment and on `Copy endpoint` to fill the following values:

ELASTICSEARCH_URL=
KIBANA_URL=
ELASTIC_APM_SERVER_ENDPOINT=
ELASTIC_APM_SERVER_RUM_ENDPOINT= // same as APM_SERVER_ENDPOINT

> NOTE copying the endpoint will not add the necessary port (443) to the end of the URL, make sure to add it (see example .env below)

3. from `https://YOUR_DEPLOYMENT.elastic-cloud.com/app/management/security/api_keys/` click on `Create API Key`:

ELASTICSEARCH_APIKEY=

4. from `https://YOUR_DEPLOYMENT.elastic-cloud.com/app/home#/tutorial/apm` copy the `OTEL_EXPORTER_OTLP_HEADERS` value:

ELASTIC_APM_SERVER_SECRET=

5. other values:

ELASTIC_APM_SERVER_RUM_CREDENTIALS=false
BACKLOAD_DATA=false
DELETE_DATA=false

### Example .env with all values

ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=abcde12345!

ELASTICSEARCH_URL=https://YOUR_DEPLOYMENT.es.us-east-2.aws.elastic-cloud.com
KIBANA_URL=https://YOUR_DEPLOYMENT.kb.us-east-2.aws.elastic-cloud.com
ELASTIC_APM_SERVER_ENDPOINT=https://YOUR_DEPLOYMENT.apm.us-east-2.aws.elastic-cloud.com:443
ELASTIC_APM_SERVER_RUM_ENDPOINT=https://YOUR_DEPLOYMENT.apm.us-east-2.aws.elastic-cloud.com:443

ELASTICSEARCH_APIKEY=AIOHSJoijaODHASUDHASIDuasdasiIAOI==
ELASTIC_APM_SERVER_SECRET=AOSPDAPSIODAOospaos

ELASTIC_APM_SERVER_RUM_CREDENTIALS=false
BACKLOAD_DATA=false
DELETE_DATA=false

### Export env values so Docker can access them

`export $(cat .env | xargs)`

### Build

`docker compose build`

### Run

`docker compose up`