echo "load slos"
for i in *.json; do
    filename=$(basename -- "$i")
    extension="${filename##*.}"
    filename="${filename%.*}"
    echo $i
    curl -XPUT -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/_ml/anomaly_detectors/$filename" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d @${i}
    curl -XPOST -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/_ml/anomaly_detectors/$filename/_open" -H "kbn-xsrf: reporting"
    curl -XPOST -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" "$ELASTICSEARCH_URL/_ml/datafeeds/datafeed-$filename/_start" -H "kbn-xsrf: reporting"
done