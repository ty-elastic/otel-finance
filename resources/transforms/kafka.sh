curl -XDELETE "$ELASTICSEARCH_URL/_transform/duration-stats-1m2" -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" -H "kbn-xsrf: reporting" -H "Content-Type: application/json"
curl -XDELETE "$ELASTICSEARCH_URL/kafka-traces" -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY"

curl -XPUT "$ELASTICSEARCH_URL/_transform/duration-stats-1m2" -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d @kafka.json

