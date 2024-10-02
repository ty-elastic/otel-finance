export $(cat ../.env | xargs)
echo "create aliases"

curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/traces-apm-default/_alias/traces-apm-trader" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d'
{
  "filter": {
    "term": {
      "service.name": "trader"
    }
  }
}'

echo "load kibana resources"
curl -XPOST -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$KIBANA_URL/api/saved_objects/_import?overwrite=true&compatibilityMode=true" -H "kbn-xsrf: true" --form file=@dashboards.ndjson

echo "load frontend source map"
rm -rf build
mkdir -p build
cd build


# cd ../src/frontend
# docker build --build-arg ELASTIC_APM_SERVER_RUM_ENDPOINT=$ELASTIC_APM_SERVER_RUM_ENDPOINT --build-arg ELASTIC_APM_SERVER_RUM_CREDENTIALS=$ELASTIC_APM_SERVER_RUM_CREDENTIALS --build-arg ELASTIC_APM_DEPLOYMENT_ENVIRONMENT=$ELASTIC_APM_DEPLOYMENT_ENVIRONMENT -t frontend .
# cd ../../elasticsearch/build


id=$(docker create otel-apm-ml-frontend)
docker cp $id:/usr/share/nginx/html/static/js .
docker rm -v $id

SERVICE_VERSION=1.0.0
SERVICE_NAME=trader-app
for i in js/*.map; do
  echo "${i}"
  curl -X POST "$KIBANA_URL/api/apm/sourcemaps" \
  -H 'Content-Type: multipart/form-data' \
  -H 'kbn-xsrf: true' \
  -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" \
  -F "service_name=${SERVICE_NAME}" \
  -F "service_version=${SERVICE_VERSION}" \
  -F "bundle_filepath=/static/${i}" \
  -F "sourcemap=@${i}"
done

