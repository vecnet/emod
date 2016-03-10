# Copyright (C) 2015, University of Notre Dame
# All rights reserved

from fabric.api import local, sudo

def update():
    local("sudo chown -R $USER:apache website/media")
    local("chmod 775 -R website/media")
    local('git pull')
    local('pip install -r requirements.txt')
    local('python manage.py migrate')
    local("sudo chown $USER:apache db.sqlite3")
    local("chmod 775 db.sqlite3")
    local('python manage.py collectstatic --noinput')
    # Update crontab jobs (using django-crontab application)
    local('python manage.py crontab add')
    local('touch wsgi.py')



