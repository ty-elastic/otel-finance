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

####################################################################### CONDITIONS

if [ -z "$_SANDBOX_ID" ]; then
  # only for image testing
  export _SANDBOX_ID=$(openssl rand -hex 9)
else
  echo "Wait for the Instruqt host bootstrap to finish"
  # Wait for the Instruqt host bootstrap to finish
  retry_command test -f /opt/instruqt/bootstrap/host-bootstrap-completed
fi

echo "Wait for the Kubernetes API server to become available"
# Wait for the Kubernetes API server to become available
retry_command curl --silent --fail --output /dev/null http://localhost:8001/api

# Wait for Elasticsearch to be created and ready
echo 'Waiting for Elasticsearch'
retry_command kubectl get pods -n default | grep -q elasticsearch
echo 'Waiting for Kibana'
retry_command kubectl get pods -n default | grep -q kibana
echo 'Waiting for Elasticsearch to be ready'
retry_command kubectl wait pod -n default -l common.k8s.elastic.co/type --for=condition=Ready --timeout=30s

####################################################################### ECK

echo 'ELASTIC_APM_SERVER_RUM_ENDPOINT="https://'$HOSTNAME'-8200-'$_SANDBOX_ID'.env.play.instruqt.com"' >> /root/.env

export $(cat /root/.env | xargs) 

ELASTICSEARCH_AUTH_BASE64=$(echo -n "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" | base64)

# Start trial license
echo "obtain trial license"
retry_command curl -s -X POST --header "Authorization: Basic $ELASTICSEARCH_AUTH_BASE64" \
"$ELASTICSEARCH_URL_LOCAL/_license/start_trial?acknowledge=true"
echo "trial license obtained and applied"

####################################################################### INGRESS

echo "configure ingress"

echo '
---

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: apm-ing
  namespace: default
  annotations:
    kubernetes.io/ingress.class: traefik
spec:
  rules:
  - host: "apm.kubernetes-vm.$_SANDBOX_ID.instruqt.io"
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: apm-lb
            port:
              number: 8200
' > /root/ingress-apm.yaml

envsubst < /root/ingress-apm.yaml | kubectl apply -f -

# ingress route for kibana

echo '
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: kibana-ing
  namespace: default
spec:
  entryPoints:
    - websecure
  routes:
  - match: Host(`kibana.kubernetes-vm.$_SANDBOX_ID.instruqt.io`) && PathPrefix(`/`)
    kind: Rule
    services:
    - name: kibana-lb
      port: 5601
    middlewares:
    - name: set-upstream-basic-auth
' > /root/ingress-kibana.yaml

envsubst < /root/ingress-kibana.yaml | kubectl apply -f -

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
        \"userEmail\": \"$INSTRUQT_USER_EMAIL\"
      }
    }")

    OPENAI_APIKEY=$(echo $output | jq -r '.key')

    if [ -z "${OPENAI_APIKEY}" ]; then
        echo "Failed to extract API key from response on attempt $attempt"
        return 1
    else
        echo "Request successful and API key extracted on attempt $attempt"
        echo 'OPENAI_APIKEY="'$OPENAI_APIKEY'"' >> /root/.env
        return 0
    fi
}
retry_command get_openai_key

if [ -z "${LLM_SKIP_ES_CONNECTION}" ]; then
  echo "Adding OpenAI connector"
  add_connector() {
      local http_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$KIBANA_URL_LOCAL/api/actions/connector" \
      -H 'Content-Type: application/json' \
      --header "kbn-xsrf: true" --header "Authorization: Basic $ELASTICSEARCH_AUTH_BASE64" -d'
      {
        "name":"openai-connector",
        "config": {
          "apiProvider":"OpenAI",
          "apiUrl":"https://'"$LLM_PROXY_URL"'/v1/chat/completions",
          "defaultModel": "gpt-4o"
        },
        "secrets": {
          "apiKey": "'"$OPENAI_APIKEY"'"
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

