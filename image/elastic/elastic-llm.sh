#!/bin/bash

####################################################################### SCRIPTS

# Function to retry a command with exponential backoff
retry_command() {
    local max_attempts=8
    local timeout=1
    local attempt=1
    local exit_code=0

    while [ $attempt -le $max_attempts ]
    do
        "$@"
        exit_code=$?

        if [ $exit_code -eq 0 ]; then
            break
        fi

        echo "Attempt $attempt failed! Retrying in $timeout seconds..."
        sleep $timeout
        attempt=$(( attempt + 1 ))
        timeout=$(( timeout * 2 ))
    done

    if [ $exit_code -ne 0 ]; then
        echo "Command $@ failed after $attempt attempts!"
    fi

    return $exit_code
}

####################################################################### ENV

export $(cat /root/.env | xargs) 

ELASTICSEARCH_AUTH_BASE64=$(echo -n "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" | base64)

####################################################################### OPENAI
# Request API key from LLM Proxy

echo "Getting OpenAI Key"
get_openai_key() {
    output=$(curl -X POST -s "https://$LLM_PROXY_URL/key/generate" \
    -H "Authorization: Bearer $SA_LLM_PROXY_BEARER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"models\": $LLM_MODELS,
      \"duration\": \"$LLM_KEY_DURATION\",
      \"key_alias\": \"instruqt-$_SANDBOX_ID\",
      \"max_budget\": $LLM_KEY_MAX_BUDGET,
      \"metadata\": {
        \"workshopId\": \"$WORKSHOP_KEY\",
        \"inviteId\": \"$INSTRUQT_TRACK_INVITE_ID\",
        \"userId\": \"$INSTRUQT_USER_ID\",
        \"userEmail\": \"$INSTRUQT_USER_EMAIL\",
        \"purpose\": \"workshop\"
      }
    }")

    LLM_APIKEY=$(echo $output | jq -r '.key')

    if [[ $LLM_APIKEY = sk-* ]]; then
        echo "Request successful and API key extracted on attempt $attempt"
        return 0
    else
        echo "Failed to extract API key from $LLM_PROXY_URL on attempt $attempt: $output"
        return 1
    fi
}
retry_command get_openai_key

echo 'LLM_APIKEY="'$LLM_APIKEY'"' >> /root/.env

LLM_MODEL="${$1:LLM_DEFAULT_MODEL}" 

if [ "$LLM_MODEL" != "none" ]; then
  echo "Adding LLM connector"

  add_connector() {
      local http_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$KIBANA_URL_LOCAL/api/actions/connector" \
      -H 'Content-Type: application/json' \
      --header "kbn-xsrf: true" --header "Authorization: Basic $ELASTICSEARCH_AUTH_BASE64" -d'
      {
        "name":"openai-connector",
        "config": {
          "apiProvider":"OpenAI",
          "apiUrl":"https://'"$LLM_PROXY_URL"'/v1/chat/completions",
          "defaultModel": "'"$LLM_MODEL"'"
        },
        "secrets": {
          "apiKey": "'"$LLM_APIKEY"'"
        },
        "connector_type_id":".gen-ai"
      }')

      if echo $http_status | grep -q '^2'; then
          echo "Connector added successfully with HTTP status: $http_status"
          return 0
      else
          echo "Failed to add connector. HTTP status: $http_status"
          return 1
      fi
  }
  retry_command add_connector
fi

# init knowledgebase
echo "Initializing knowledgebase"
init_kb() {
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$KIBANA_URL_LOCAL/internal/observability_ai_assistant/kb/setup" \
    -H 'Content-Type: application/json' \
    --header "kbn-xsrf: true" --header "Authorization: Basic $ELASTICSEARCH_AUTH_BASE64")

    if echo $http_status | grep -q '^2'; then
        echo "Elastic knowledgebase successfully initialized: $http_status"
        return 0
    else
        echo "Failed to initialize Elastic knowledgebase. HTTP status: $http_status"
        return 1
    fi
}
retry_command init_kb
