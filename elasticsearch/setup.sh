export ELASTICSEARCH_URL="https://${ES_USER}:${ES_PASS}@${ES_ADDRESS}:443"
echo $ELASTICSEARCH_URL
export KIBANA_URL="https://${ES_USER}:${ES_PASS}@${KB_ADDRESS}:9243"
echo $KIBANA_URL

echo "create aliases"
curl -XDELETE "$ELASTICSEARCH_URL/traces-apm-default/_alias/traces-apm-trader" -H "kbn-xsrf: reporting"
curl -XPUT "$ELASTICSEARCH_URL/traces-apm-default/_alias/traces-apm-trader" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d'
{
  "filter": {
    "term": {
      "service.name": "trader"
    }
  }
}'

echo "load kibana resources"
#curl -XPOST "$KIBANA_URL/api/saved_objects/_import?overwrite=true&compatibilityMode=true" -H "kbn-xsrf: true" --form file=@dashboards.ndjson
curl -XPOST "$KIBANA_URL/api/saved_objects/_import?overwrite=true&compatibilityMode=true" -H "kbn-xsrf: true" --form file=@dashboards.ndjson