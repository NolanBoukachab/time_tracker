#!/bin/bash
git remote add heroku https://${HEROKU_USERNAME}:${HEROKU_TOKEN}@git.heroku.com/timetrackin.git
git push heroku main
