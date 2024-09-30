export $(cat /root/.env | xargs)
BASE64=$(echo -n "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" | base64)

echo "create aliases"
curl -XDELETE --header "Authorization: Basic $BASE64" "$ELASTICSEARCH_URL/traces-apm-default/_alias/traces-apm-trader" -H "kbn-xsrf: reporting"
curl -XPUT --header "Authorization: Basic $BASE64" "$ELASTICSEARCH_URL/traces-apm-default/_alias/traces-apm-trader" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d'
{
  "filter": {
    "term": {
      "service.name": "trader"
    }
  }
}'

echo "load kibana resources"
curl -XPOST --header "Authorization: Basic $BASE64" "$KIBANA_URL/api/saved_objects/_import?overwrite=true&compatibilityMode=true" -H "kbn-xsrf: true" --form file=@dashboards.ndjson