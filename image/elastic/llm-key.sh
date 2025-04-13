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

agent variable set LLM_KEY $LLM_APIKEY
agent variable set LLM_HOST $LLM_PROXY_URL
agent variable set LLM_CHAT_URL https://$LLM_PROXY_URL/v1/chat/completions
