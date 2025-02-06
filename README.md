# Environment Variables

Create a `.env` file with the following defined:

KIBANA_URL=

ELASTICSEARCH_URL=
ELASTICSEARCH_USER=
ELASTICSEARCH_PASSWORD=
ELASTICSEARCH_APIKEY=

ELASTIC_APM_SERVER_ENDPOINT=
ELASTIC_APM_SERVER_SECRET=
ELASTIC_APM_SERVER_RUM_ENDPOINT=
ELASTIC_APM_SERVER_RUM_CREDENTIALS=false

BACKLOAD_DATA=false
DELETE_DATA=false

`export $(cat .env | xargs)`

# Build

`docker compose build`

# Run

`docker compose up`