export $(cat ../../.env | xargs)  

echo $OPENAI_URL
echo "Adding OpenAI connector"
add_connector() {
      curl -X POST "$KIBANA_URL/api/actions/connector/c55b6eb0-6bad-11eb-9f3b-611eebc6c3ad" \
      -H 'Content-Type: application/json' \
      --header "kbn-xsrf: true" -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" -d'
      {
        "name":"openai-connector",
        "config": {
          "apiProvider":"OpenAI",
          "apiUrl":"'$OPENAI_URL'",
          "defaultModel": "gpt-4o"
        },
        "secrets": {
          "apiKey": "'"$OPENAI_KEY"'"
        },
        "connector_type_id":".gen-ai"
      }'
  }

add_connector
