
echo "load context resources"

curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/_inference/sparse_embedding/elser_model_2_linux-x86_64" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d'
{
  "service": "elser",
  "service_settings": {
    "num_allocations": 1,
    "num_threads": 1
  }
}'

for i in indicies/*.json; do
  filename=$(basename -- "$i")
  extension="${filename##*.}"
  filename="${filename%.*}"
  curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/$filename" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d @${i} 
done

for i in pipelines/*.json; do
  filename=$(basename -- "$i")
  extension="${filename##*.}"
  filename="${filename%.*}"
  curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/_ingest/pipeline/${filename}" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d @${i}
done

for i in docs/*.json; do
  filename=$(basename -- "$i")
  extension="${filename##*.}"
  filename="${filename%.*}"
  curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/search-github/_doc/${filename}?pipeline=search-github" -H "Content-Type: application/json" -d @${i}
done

for i in knowledge/*.json; do
  filename=$(basename -- "$i")
  extension="${filename##*.}"
  filename="${filename%.*}"
  curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/.kibana-observability-ai-assistant-kb-000001/_doc/${filename}?pipeline=.kibana-observability-ai-assistant-kb-ingest-pipeline" -H "Content-Type: application/json" -d @${i}
done
