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

####################################################################### ELSER
 echo "Downloading ELSER inference model"
 retry_command curl -s -X PUT --header "Authorization: Basic $ELASTICSEARCH_AUTH_BASE64"  -H 'Content-Type: application/json' \
 "$ELASTICSEARCH_URL_LOCAL/_ml/trained_models/.elser_model_2_linux-x86_64" -d'
 {
   "input":{"field_names": ["text_field"]}
 }'
 
####################################################################### ELSER
 echo "Downloading E5 inference model"
 retry_command curl -s -X PUT --header "Authorization: Basic $ELASTICSEARCH_AUTH_BASE64"  -H 'Content-Type: application/json' \
 "$ELASTICSEARCH_URL_LOCAL/_ml/trained_models/.multilingual-e5-small" -d'
 {
   "input":{"field_names": ["text_field"]}
 }'

