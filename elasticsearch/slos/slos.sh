echo "load slos"
for i in *.json; do
    filename=$(basename -- "$i")
    extension="${filename##*.}"
    filename="${filename%.*}"
    echo $i
    curl -XPOST -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$KIBANA_URL/api/observability/slos" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d @${i}
done