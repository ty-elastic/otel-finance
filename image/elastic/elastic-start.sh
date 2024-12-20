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

if [ -z "$INSTRUQT" ]; then
  echo "not running instruqt"
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

if [ -n "$INSTRUQT" ]; then
  echo 'ELASTIC_APM_SERVER_RUM_ENDPOINT="https://'$HOSTNAME'-8200-'$_SANDBOX_ID'.env.play.instruqt.com"' >> /root/.env
fi

export $(cat /root/.env | xargs) 

ELASTICSEARCH_AUTH_BASE64=$(echo -n "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" | base64)

# Start trial license
echo "obtain trial license"
retry_command curl -s -X POST --header "Authorization: Basic $ELASTICSEARCH_AUTH_BASE64" \
"$ELASTICSEARCH_URL_LOCAL/_license/start_trial?acknowledge=true"
echo "trial license obtained and applied"

####################################################################### INGRESS

if [ -n "$INSTRUQT" ]; then
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
fi