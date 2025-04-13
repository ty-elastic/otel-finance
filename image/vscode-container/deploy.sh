GCP_PROJECT_ID=elastic-sa
GCP_REGION=us-central1
GCP_LABELS="division=field,org=sa,team=genai"

# tag images with current build date
build=$(date +%F)
echo $build

arch=linux/amd64
test=false
version=$build

echo "arch=$arch"
echo "test=$test"
echo "version=$version"

IMAGE="vscode"
if [ "$test" = true ] ; then
    IMAGE="vscode.test"
fi
echo "IMAGE=$IMAGE"

deploy_image() {
    docker build --platform $arch --progress plain -t $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/instruqt/$IMAGE:$version .
    docker tag $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/instruqt/$IMAGE:$version $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/instruqt/$IMAGE:latest
    if [ "$test" = false ] ; then
        docker push $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/instruqt/$IMAGE:$version
        docker push $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/instruqt/$IMAGE:latest
    fi
}

deploy_image
