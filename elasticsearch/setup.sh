ELASTICSEARCH_URL="https://${ES_USER}:${ES_PASS}@${ES_ENDPOINT}:443"

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
