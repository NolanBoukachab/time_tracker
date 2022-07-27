#!/bin/bash

DEPLOY_PATH=/tmp/heroku-deploy-`date +%s`/

rm -rf $DEPLOY_PATH
mkdir -p $DEPLOY_PATH

cd $DEPLOY_PATH
git clone https://github.com/NolanBoukachab/time_tracker tt
cd tt
heroku git:remote -a timetrackin
git add -A .
git commit -m "deploy"
git push heroku main

cd -
rm -rf $DEPLOY_PATH

echo "🚀  https://timetrackin.herokuapp.com"
