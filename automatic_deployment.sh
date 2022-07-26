#!/bin/bash
pipenv shell
pipenv install gunicorn
echo "web: gunicorn app:app" > Procfile
sudo snap install heroku --classic
heroku login -i
echo "Nom de projet:\n"
read $projectName
heroku create $projectName
heroku git:remote -a $projectName
git add .
git commit -m "initial commit"
git push heroku master
