echo "Adding OpenAI connector"
add_azure_connector() {
      curl -X POST "$KIBANA_URL/api/actions/connector/d7e8a4a5-a2c0-4814-a397-1f0a37313ac9" \
      -H 'Content-Type: application/json' \
      --header "kbn-xsrf: true" -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" -d'
      {
        "name":"openai-connector",
        "config": {
          "apiProvider":"Azure OpenAI",
          "apiUrl":"'$OPENAI_URL'"
        },
        "secrets": {
          "apiKey": "'"$OPENAI_KEY"'"
        },
        "connector_type_id":".gen-ai"
      }'
  }

add_azure_connector