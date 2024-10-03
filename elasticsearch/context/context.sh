
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
  ID=$(echo -n  "${i}" | base64)
  curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/search-github/_doc/${ID}?pipeline=search-github" -H "Content-Type: application/json" -d @${i}
done