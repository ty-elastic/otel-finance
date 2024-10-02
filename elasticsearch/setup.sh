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

