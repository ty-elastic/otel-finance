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

#########

echo "load kibana resources"
curl -XPOST -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$KIBANA_URL/api/saved_objects/_import?overwrite=true&compatibilityMode=true" -H "kbn-xsrf: true" --form file=@dashboards/dashboards.ndjson

#########

echo "load github resources"

curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/_inference/sparse_embedding/my-elser-model" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d'
{
  "service": "elser",
  "service_settings": {
    "num_allocations": 1,
    "num_threads": 1
  }
}'

for i in github/pipelines/*.json; do
  filename=$(basename -- "$i")
  extension="${filename##*.}"
  filename="${filename%.*}"
  echo $filename
  echo $i
  curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/_ingest/pipeline/${filename}" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d @${i}
done

for i in github/docs/*.json; do
  ID=$(echo -n  "${i}" | base64)
  curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/search-github/_doc/${ID}?pipeline=search-github" -H "Content-Type: application/json" -d @${i}
done

#########

echo "setup openai"

