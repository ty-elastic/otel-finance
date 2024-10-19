for i in static/js/*.js; do
  echo "${i}"
  curl -iv --limit-rate 500K -X POST "$KIBANA_URL/api/apm/sourcemaps" \
  -H 'Content-Type: multipart/form-data' \
  -H 'kbn-xsrf: true' \
  -u "${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}" \
  -F "service_name=${SERVICE_NAME}" \
  -F "service_version=${SERVICE_VERSION}" \
  -F "bundle_filepath=/${i}" \
  -F "sourcemap=@${i}.map"
done
