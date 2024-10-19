echo $ELASTICSEARCH_USER
output=$(curl -X POST -s -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" $ELASTICSEARCH_URL/_security/api_key -H 'Content-Type: application/json' -d '{"name": "collector"}')

export ELASTICSEARCH_APIKEY=$(echo $output | jq -r '.encoded')
echo $ELASTICSEARCH_APIKEY