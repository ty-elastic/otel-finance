#!/bin/bash

####################################################################### CODE

export $(cat /root/.env | xargs)

echo 'BACKLOAD_DATA=true' >> /root/.env
echo 'SOLVE_ALL=false' >> /root/.env

echo "export $(cat /root/.env | xargs)" >> /root/.bashrc

GIT_BRANCH=main
GIT_URL=https://github.com/ty-elastic/otel-finance.git

cd $WORKSPACE_DIR
git config --global init.defaultBranch $GIT_BRANCH
git init
git remote add origin $GIT_URL
git pull
git checkout $GIT_BRANCH -f
git branch --set-upstream-to origin/$GIT_BRANCH

mkdir -p $WORKSPACE_DIR/logs

echo "cd $WORKSPACE_DIR" >> /root/.bashrc

docker compose build
