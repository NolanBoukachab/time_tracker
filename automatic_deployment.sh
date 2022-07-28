#!/bin/bash
echo ${HEROKU_USERNAME}
echo ${HEROKU_TOKEN}
echo ${"Test"}
git remote add heroku https://${HEROKU_USERNAME}:${HEROKU_TOKEN}@git.herokuapp.com/timetrackin
git push heroku main
