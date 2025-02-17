#!/bin/bash

####################################################################### DOCKER

for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get -y install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

####################################################################### CODE

WORKSPACE_DIR=/workspace
echo "WORKSPACE_DIR=$WORKSPACE_DIR" >> /root/.env

export $(cat /root/.env | xargs)
echo "export $(cat /root/.env | xargs)" >> /root/.bashrc

GIT_BRANCH=main
GIT_URL=https://github.com/ty-elastic/otel-finance.git

mkdir -p $WORKSPACE_DIR

cd $WORKSPACE_DIR
git config --global init.defaultBranch $GIT_BRANCH
git init
git remote add origin $GIT_URL
git pull
git checkout $GIT_BRANCH -f
git branch --set-upstream-to origin/$GIT_BRANCH

mkdir -p $WORKSPACE_DIR/logs

docker compose -f docker-compose-playback.yml build
docker compose -f docker-compose-playback.yml pull

