#!/bin/bash

DEPLOY_PATH=/tmp/heroku-deploy-`date +%s`/
HEROKU_NAME="$1"

rm -rf $DEPLOY_PATH
mkdir -p $DEPLOY_PATH

cd $DEPLOY_PATH
git init
heroku git:remote -a $HEROKU_NAME
echo "1"
git add -A .
echo "2"
git commit -m "deploy"
echo "33"
git push --force heroku master
echo "4"

cd -
rm -rf $DEPLOY_PATH

echo "🚀  https://$HEROKU_NAME"
