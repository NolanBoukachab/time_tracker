#!/bin/bash

DEPLOY_PATH=/tmp/heroku-deploy-`date +%s`/

rm -rf $DEPLOY_PATH
mkdir -p $DEPLOY_PATH

cd $DEPLOY_PATH
git clone https://github.com/NolanBoukachab/time_tracker tt
echo "1"
cd tt
echo "11"
heroku git:remote -a $1
echo "2"
git add -A .
echo "3"
git commit -m "deploy"
echo "4"
git push heroku main

cd -
rm -rf $DEPLOY_PATH

echo "🚀  https://$1.herokuapp.com"
