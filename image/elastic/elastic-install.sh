#!/bin/bash

####################################################################### STARTUP

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

echo "Wait for the Kubernetes API server to become available"
# Wait for the Kubernetes API server to become available
retry_command curl --silent --fail --output /dev/null http://localhost:8001/api

####################################################################### ECK

ELASTICSEARCH_PASSWORD=$(openssl rand -hex 9)
APM_SECRET_TOKEN=$(openssl rand -hex 9)

# Apply Elastic resources
kubectl create -f https://download.elastic.co/downloads/eck/$ELASTIC_ECK_VERSION/crds.yaml
kubectl apply -f https://download.elastic.co/downloads/eck/$ELASTIC_ECK_VERSION/operator.yaml

kubectl create secret generic elasticsearch-es-elastic-user --from-literal=elastic=$ELASTICSEARCH_PASSWORD

# Apply Elastic resources (Kibana, Elasticsearch, Services)
cat <<EOF | kubectl apply -f -
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: kibana
  namespace: default
spec:
  version: $ELASTIC_STACK_VERSION
  count: 1
  elasticsearchRef:
    name: elasticsearch
  http:
    tls:
      selfSignedCertificate:
        disabled: true
  config:
    # required to allow symbol upload from APM javascript
    server.maxPayload: 4194304
    server.publicBaseUrl: http://localhost:30002
    telemetry.optIn: false
    telemetry.allowChangingOptInStatus: false
    xpack.fleet.agents.elasticsearch.hosts: ["http://elasticsearch-es-http.default.svc:9200"]
    xpack.fleet.agents.fleet_server.hosts: ["https://fleet-server-agent-http.default.svc:8220"]
    xpack.fleet.packages:
    - name: system
      version: latest
    - name: elastic_agent
      version: latest
    - name: fleet_server
      version: latest
    - name: apm
      version: latest
    xpack.fleet.agentPolicies:
    - name: Fleet Server on ECK policy
      id: eck-fleet-server
      namespace: default
      #monitoring_enabled:
      #- logs
      #- metrics
      unenroll_timeout: 900
      package_policies:
      - name: fleet_server-1
        id: fleet_server-1
        package:
          name: fleet_server
    - name: Elastic Agent on ECK policy
      id: policy-elastic-agent-on-cloud
      namespace: default
      #monitoring_enabled:
      #- logs
      #- metrics
      unenroll_timeout: 900
      package_policies:
      - name: system-1
        id: system-1
        package:
          name: system
      - package:
          name: apm
        name: apm-1
        inputs:
        - type: apm
          enabled: true
          vars:
          - name: host
            value: 0.0.0.0:8200 
          - name: url
            value: "https://apm.default.svc:8200" 
          - name: secret_token
            value: $APM_SECRET_TOKEN    
---
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: elasticsearch
  namespace: default
spec:
  version: $ELASTIC_STACK_VERSION
  http:
    tls:
      selfSignedCertificate:
        disabled: true
  nodeSets:
  - name: default
    count: 1
    config:
      node.store.allow_mmap: false
      # default is 30, but we need a bit more capacity for elser
      xpack.ml.max_machine_memory_percent: 45
    podTemplate:
      spec:
        initContainers:
        - name: sysctl
          securityContext:
            privileged: true
            runAsUser: 0
          command: ['sh', '-c', 'sysctl -w vm.max_map_count=262144']
        containers:
        - name: elasticsearch
          resources:
            requests:
              memory: 8Gi
            limits:
              memory: 8Gi
---
apiVersion: agent.k8s.elastic.co/v1alpha1
kind: Agent
metadata:
  name: fleet-server
  namespace: default
spec:
  version: $ELASTIC_STACK_VERSION
  kibanaRef:
    name: kibana
  elasticsearchRefs:
  - name: elasticsearch
  mode: fleet
  fleetServerEnabled: true
  policyID: eck-fleet-server
  deployment:
    replicas: 1
    podTemplate:
      spec:
        serviceAccountName: fleet-server
        automountServiceAccountToken: true
        securityContext:
          runAsUser: 0
        containers:
        - name: agent
          resources:
            requests:
              memory: 300Mi
              cpu: 0.2
            limits:
              memory: 1000Mi
              cpu: 1
---
apiVersion: agent.k8s.elastic.co/v1alpha1
kind: Agent
metadata: 
  name: elastic-agent
  namespace: default
spec:
  version: $ELASTIC_STACK_VERSION
  kibanaRef:
    name: kibana
  fleetServerRef: 
    name: fleet-server
  mode: fleet
  policyID: policy-elastic-agent-on-cloud
  image: docker.elastic.co/beats/elastic-agent-complete:$ELASTIC_STACK_VERSION
  deployment:
    replicas: 1
    podTemplate:
      spec:
        securityContext:
          runAsUser: 1000
        volumes:
        - emptyDir: {}
          name: agent-data
        containers:
        - name: agent
          resources:
            requests:
              memory: 300Mi
              cpu: 0.2
            limits:
              memory: 2000Mi
              cpu: 2
---
apiVersion: v1
kind: Service
metadata:
  name: apm
  namespace: default
spec:
  selector:
    agent.k8s.elastic.co/name: elastic-agent
  ports:
  - protocol: TCP
    port: 30820
---
apiVersion: v1
kind: Service
metadata:
  name: kibana
  namespace: default
spec:
  selector:
    kibana.k8s.elastic.co/name: kibana
  ports:
  - protocol: TCP
    nodePort: 30002
    port: 5601
  type: NodePort
---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
  namespace: default
spec:
  selector:
    elasticsearch.k8s.elastic.co/cluster-name: elasticsearch
  ports:
  - protocol: TCP
    nodePort: 30920
    port: 9200
  type: NodePort
---
apiVersion: v1
kind: Service
metadata:
  name: apm-nodeport
  namespace: default
spec:
  selector:
    agent.k8s.elastic.co/name: elastic-agent
  ports:
  - protocol: TCP
    nodePort: 30820
    port: 8200
  type: NodePort
---
apiVersion: v1
kind: Service
metadata:
  name: apm-service
  namespace: default
spec:
  selector:
    agent.k8s.elastic.co/name: elastic-agent
  ports:
  - protocol: TCP
    port: 8200
    targetPort: 8200
---
apiVersion: v1
kind: Service
metadata:
  name: fleet-nodeport
  namespace: default
spec:
  selector:
    agent.k8s.elastic.co/name: fleet-server
    common.k8s.elastic.co/type: agent
  ports:
  - protocol: TCP
    nodePort: 30822
    port: 8220
  type: NodePort
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fleet-server
rules:
- apiGroups: [""]
  resources:
  - pods
  - namespaces
  - nodes
  verbs:
  - get
  - watch
  - list
- apiGroups: ["coordination.k8s.io"]
  resources:
  - leases
  verbs:
  - get
  - create
  - update
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fleet-server
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: fleet-server
subjects:
- kind: ServiceAccount
  name: fleet-server
  namespace: default
roleRef:
  kind: ClusterRole
  name: fleet-server
  apiGroup: rbac.authorization.k8s.io
EOF

# Wait for Elasticsearch to be created and ready
echo 'Waiting for Elasticsearch'
retry_command kubectl get pods -n default | grep -q elasticsearch
echo 'Waiting for Elasticsearch to be ready'
retry_command kubectl wait pod -n default -l common.k8s.elastic.co/type --for=condition=Ready --timeout=30s

# Wait for Kibana to be created and ready
echo 'Waiting for Kibana'
retry_command kubectl get pods -n default | grep -q kibana
echo 'Waiting for all pods to be ready'
retry_command kubectl wait pod -n default -l common.k8s.elastic.co/type --for=condition=Ready --timeout=300s

echo 'waiting for fleet-server'
retry_command kubectl get pods -n default | grep -q fleet-server 
echo 'Waiting for all pods to be ready'
retry_command kubectl wait pod -n default -l common.k8s.elastic.co/type --for=condition=Ready --timeout=300s

echo 'waiting for elastic-agent'
retry_command kubectl get pods -n default | grep -q elastic-agent 
echo 'Waiting for all pods to be ready'
retry_command kubectl wait pod -n default -l common.k8s.elastic.co/type --for=condition=Ready --timeout=300s

# Set up environment variables
echo 'ELASTICSEARCH_USER=elastic' >> /root/.env
echo -n 'ELASTICSEARCH_PASSWORD=' >> /root/.env
kubectl get secret elasticsearch-es-elastic-user -n default -o go-template='{{.data.elastic | base64decode}}' >> /root/.env
echo '' >> /root/.env
echo 'ELASTIC_VERSION="'$ELASTIC_STACK_VERSION'"' >> /root/.env

echo 'ELASTICSEARCH_URL_LOCAL="http://localhost:30920"' >> /root/.env
echo 'KIBANA_URL_LOCAL="http://localhost:30002"' >> /root/.env

echo 'ELASTIC_APM_SERVER_SECRET='$APM_SECRET_TOKEN >> /root/.env
echo 'ELASTIC_APM_SERVER_RUM_CREDENTIALS=true' >> /root/.env

echo 'ELASTICSEARCH_URL="http://172.17.0.1:30920"' >> /root/.env
echo 'ELASTIC_APM_SERVER_ENDPOINT="http://172.17.0.1:8200"' >> /root/.env
echo 'KIBANA_URL="http://172.17.0.1:30002"' >> /root/.env

export $(cat /root/.env | xargs) 

BASE64=$(echo -n "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" | base64)
KIBANA_URL_WITHOUT_PROTOCOL=$(echo $KIBANA_URL_LOCAL | sed -e 's#http[s]\?://##g')

# Create API Key
echo "Create API key"
create_api_key() {
    output=$(curl -s -X POST "$ELASTICSEARCH_URL_LOCAL/_security/api_key" \
    -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" \
    -H "Content-Type: application/json" \
    -d '{"name": "collector"}')

    ELASTICSEARCH_APIKEY=$(echo $output | jq -r '.encoded')

    if [ -z "${ELASTICSEARCH_APIKEY}" ]; then
        echo "Failed to generate elastic apikey on attempt $attempt"
        return 1
    else
        echo "Request successful and elastic apikey extracted on attempt $attempt"
        return 0
    fi
}
retry_command create_api_key
echo 'ELASTICSEARCH_APIKEY="'$ELASTICSEARCH_APIKEY'"' >> /root/.env

####################################################################### NGINX

# Install nginx
echo "Install NGINX"
{ apt-get update; apt-get install nginx -y; } 

# Configure nginx
echo '
upstream keepalive-upstream {
  server '${KIBANA_URL_WITHOUT_PROTOCOL}';
  server '${KIBANA_URL_WITHOUT_PROTOCOL}';
  server '${KIBANA_URL_WITHOUT_PROTOCOL}';
  keepalive 64;
}

server { 
  listen 30001 default_server;
  server_name kibana;
  location /nginx_status {
    stub_status on;
    allow 127.0.0.1;
    deny all;
  }
  location / {
    proxy_set_header Host '${KIBANA_URL_WITHOUT_PROTOCOL}';
    proxy_pass http://keepalive-upstream;
    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    proxy_set_header Connection "";
    proxy_hide_header Content-Security-Policy;
    proxy_set_header X-Scheme $scheme;
    proxy_set_header Authorization "Basic '${BASE64}'";
    proxy_set_header Accept-Encoding "";
    proxy_redirect off;
    proxy_http_version 1.1;
    client_max_body_size 20M;
    proxy_read_timeout 600;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains;";
    proxy_send_timeout          300;
    send_timeout                300;
    proxy_connect_timeout       300;
 }
}

server {
  listen 9200;
  server_name elasticsearch;
  
  location / {
    proxy_pass http://localhost:30920;
    proxy_connect_timeout       300;
    proxy_send_timeout          300;
    proxy_read_timeout          300;
    send_timeout                300;
  }
}

upstream fleet-upstream {
  server localhost:30822;
  server localhost:30822;
  server localhost:30822;
}

server {
  listen 8220 ssl;
  
  server_name fleet-server;
  ssl_certificate /etc/ssl/certs/nginx-selfsined.crt;
  ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

  location / {
    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    proxy_pass https://fleet-upstream;
    proxy_connect_timeout       300;
    proxy_send_timeout          300;
    proxy_read_timeout          300;
    send_timeout                300;
  }
}
' > /etc/nginx/conf.d/default.conf

echo '127.0.0.1 fleet-server-agent-http.default.svc' >> /etc/hosts
echo '127.0.0.1 elasticsearch-es-http.default.svc' >> /etc/hosts

sudo mkdir /etc/ssl/private
sudo chmod 700 /etc/ssl/private

sudo openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
    -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=fleet-server-agent-http.default.svc" \
    -keyout /etc/ssl/private/nginx-selfsigned.key  -out /etc/ssl/certs/nginx-selfsined.crt

echo "Restart NGINX"
systemctl enable nginx
systemctl restart nginx


####################################################################### INGRESS

echo "configure ingress"

echo '
apiVersion: v1
kind: Service
metadata:
  name: apm-lb
  namespace: default
spec:
  ports:
  - name: apm-lb
    port: 8200
    protocol: TCP
    targetPort: 8200
  selector:
    agent.k8s.elastic.co/name: elastic-agent
  type: LoadBalancer
' > /root/apm-lb.yaml

kubectl apply -f /root/apm-lb.yaml

echo '
apiVersion: v1
kind: Service
metadata:
  name: kibana-lb
  namespace: default
spec:
  ports:
  - name: kibana-lb
    port: 5601
    protocol: TCP
    targetPort: 5601
  selector:
    kibana.k8s.elastic.co/name: kibana
  type: LoadBalancer
' > /root/kibana-lb.yaml

kubectl apply -f /root/kibana-lb.yaml

kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v2.10/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml

# middleware that sets request and response header to dummy value
echo '
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: set-upstream-basic-auth
spec:
  headers:
    customRequestHeaders:
      X-Request-Id: "123"
      Authorization: "Basic $ELASTICSEARCH_AUTH_BASE64"
    customResponseHeaders:
      X-Response-Id: "4567"
' > /root/middleware.yaml

envsubst < /root/middleware.yaml | kubectl apply -f -

####################################################################### RUNTIME SERVICE

systemctl daemon-reload
systemctl enable elastic-start