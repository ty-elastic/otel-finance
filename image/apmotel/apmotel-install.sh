#!/bin/bash

####################################################################### ENVs

export $(cat /root/.env | xargs)

echo 'GIT_BRANCH=main' >> /root/.env
echo 'GIT_URL=https://github.com/ty-elastic/otel-finance.git' >> /root/.env

####################################################################### CODE

export $(cat /root/.env | xargs)

cd $WORKSPACE_DIR
git config --global init.defaultBranch $GIT_BRANCH
git init
git remote add origin $GIT_URL
git pull
git checkout $GIT_BRANCH -f
git branch --set-upstream-to origin/$GIT_BRANCH

mkdir -p $WORKSPACE_DIR/logs

docker compose build
docker compose pull
