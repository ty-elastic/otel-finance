arch=linux/amd64
cd ../../../resources
docker build --platform $arch --progress plain -t us-central1-docker.pkg.dev/elastic-sa/tbekiares/resources:rca-ai-v1 .
docker push us-central1-docker.pkg.dev/elastic-sa/tbekiares/resources:rca-ai-v1

