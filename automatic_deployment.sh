#!/bin/bash

# Usage:
# $ ./heroku-deploy.sh <app name> <git repo url> <heroku api key>

APP="$1"
REPO="$2"
APIKEY="$3"
echo "-----> Creating application $APP"
curl -u ":$APIKEY" -d "app[name]=$APP" -X POST https://api.heroku.com/apps -s > /dev/null
echo "-----> Generating bootstrap script"
BOOTSTRAPPER=$(cat<<SCRIPT
  mkdir -p ~/.ssh
  cat <<EOF > ~/.ssh/config
    Host heroku.com
        UserKnownHostsFile=/dev/null
        StrictHostKeyChecking=no
EOF
    ssh-keygen -t dsa -N "" -f /app/.ssh/id_dsa -C "heroku-deploy.sh"
    curl -u ":$APIKEY" -d @/app/.ssh/id_dsa.pub -X POST https://api.heroku.com/user/keys
    git clone $REPO repo
    cd repo
    git remote add heroku "git@heroku.com:$APP.git"
    git push heroku master
    curl -u ":$APIKEY" -X DELETE https://api.heroku.com/user/keys/heroku-deploy%2Esh
SCRIPT
)
echo "-----> Running bootstrap script on Heroku"
curl -u ":$APIKEY" -F "command=$BOOTSTRAPPER" -X POST https://api.heroku.com/apps/$APP/ps -s > /dev/null
echo "       Bootstrap script is now deploying code from $REPO"
sleep 50
echo
echo "-----> Application should be running momentarily at:"
echo "       http://$APP.herokuapp.com"
echo
