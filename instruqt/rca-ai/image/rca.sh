
source /opt/workshops/elastic-retry.sh

export $(curl http://kubernetes-vm:9000/env | xargs)

kubectl create namespace rcaai

echo '
elasticsearch-url='$ELASTICSEARCH_URL'
elasticsearch-user='$ELASTICSEARCH_USER'
elasticsearch-password='$ELASTICSEARCH_PASSWORD'
elasticsearch-apikey='$ELASTICSEARCH_APIKEY'
apmserver-endpoint='$ELASTIC_APM_SERVER_ENDPOINT'
apmserver-secret='$ELASTIC_APM_SERVER_SECRET'
kibana-url='$KIBANA_URL'
' > /root/rcaai-secrets.yaml
kubectl create secret generic elastic-environment -n rcaai --from-env-file=/root/rcaai-secrets.yaml

echo '
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |-
    extensions:
      health_check:

    receivers:
      otlp/json:
        protocols:
          http:
            endpoint: 0.0.0.0:4318

    processors:
      batch:
        send_batch_size: 1000
        send_batch_max_size: 1000
      resourcedetection:
        detectors: ["system"]
        system:
          hostname_sources: ["os"]
          resource_attributes:
            host.name:
              enabled: true
            host.id:
              enabled: false
            host.arch:
              enabled: true
            host.ip:
              enabled: true
            host.mac:
              enabled: true
            host.cpu.vendor.id:
              enabled: true
            host.cpu.family:
              enabled: true
            host.cpu.model.id:
              enabled: true
            host.cpu.model.name:
              enabled: true
            host.cpu.stepping:
              enabled: true
            host.cpu.cache.l2.size:
              enabled: true
            os.description:
              enabled: true
            os.type:
              enabled: true

    exporters:
      debug:
        verbosity: detailed

      otlp/apm: 
        endpoint: "${ELASTIC_APM_SERVER_ENDPOINT}"
        tls:
          insecure: true
        headers:
          # Elastic APM Server secret token
          Authorization: "Bearer ${ELASTIC_APM_SERVER_SECRET}"

    service:
      extensions: [health_check]
      pipelines:
        traces/apm:
          receivers: [otlp/json]
          processors: [resourcedetection, batch]
          exporters: [otlp/apm]

        metrics/apm:
          receivers: [otlp/json]
          processors: [resourcedetection, batch]
          exporters: [otlp/apm]

        logs/apm:
          receivers: [otlp/json]
          processors: [resourcedetection, batch]
          exporters: [otlp/apm]

---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  labels:
    app: rcaai
    service: collector_playback
  name: collector_playback
  namespace: rcaai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rcaai
      service: collector_playback
  template:
    metadata:
      labels:
        app: rcaai
        service: collector_playback
    spec:
      containers:
      - name: collector_playback
        image: otel/opentelemetry-collector-contrib:0.123.0
        #imagePullPolicy: Never
        command:
          - "/otel"
          - "--config=/conf/otel-collector-config.yaml"
        ports:
          - containerPort: 4318
          - containerPort: 13133
        env:
          - name: ELASTIC_APM_SERVER_ENDPOINT
            valueFrom:
              secretKeyRef:
                name: elastic-environment
                key: apmserver-endpoint
          - name: ELASTIC_APM_SERVER_SECRET
            valueFrom:
              secretKeyRef:
                name: elastic-environment
                key: apmserver-secret
        volumeMounts:
        - mountPath: /etc/otelcol-contrib/config.yaml
          name: data
          subPath: config.yaml
          readOnly: true
      terminationGracePeriodSeconds: 30
      volumes:
      - name: data
        configMap:
          name: otel-collector-config
    restartPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: rcaai
    service: collector_playback
  name: collector_playback
  namespace: rcaai
spec:
  ports:
    - name: json
      port: 4318
      targetPort: 4318
    - name: hc
      port: 13133
      targetPort: 13133
  selector:
    app: rcaai
    service: collector_playback
---
' > /root/rcaai-collector.yaml
kubectl apply -f /root/rcaai-collector.yaml

echo '
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: rcaai
    service: resources
  name: resources
  namespace: rcaai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rcaai
      service: resources
  template:
    metadata:
      labels:
        app: rcaai
        service: resources
    spec:
      initContainers:
      - name: init-curl
        image: curlimages/curl
        command: ["sh", "-c", "until curl -s --fail http://collector_playback:13133/; do echo waiting for collector; sleep 2; done"]
      containers:
      - name: resources
        image: us-central1-docker.pkg.dev/elastic-sa/tbekiares/resources:rca-ai-v1
        #imagePullPolicy: Never
        ports:
          - containerPort: 9010
        env:
          - name: BACKLOAD_DATA
            value: true
          - name: SOLVE_ALL
            value: true
          - name: ERRORS_LATENCY
            value: false
          - name: ERRORS_DB
            value: false
          - name: DELETE_DATA
            value: false

          - name: ELASTICSEARCH_USER
            valueFrom:
              secretKeyRef:
                name: elastic-environment
                key: elasticsearch-user
          - name: ELASTICSEARCH_PASSWORD
            valueFrom:
              secretKeyRef:
                name: elastic-environment
                key: elasticsearch-password
          - name: ELASTICSEARCH_URL
            valueFrom:
              secretKeyRef:
                name: elastic-environment
                key: elasticsearch-url
          - name: KIBANA_URL
            valueFrom:
              secretKeyRef:
                name: elastic-environment
                key: kibana-url

          - name: OTEL_EXPORTER_OTLP_ENDPOINT_PLAYBACK_APM
            value: "http://collector_playback:4318"
      restartPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: rcaai
    service: resources
  name: resources
  namespace: rcaai
spec:
  ports:
    - name: resources
      port: 9010
      targetPort: 9010
  selector:
    app: rcaai
    service: resources
---
' > /root/rcaai-apps.yaml
kubectl apply -f /root/rcaai-apps.yaml


