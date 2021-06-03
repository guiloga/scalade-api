#!/bin/bash

############################
# Development Installation #
############################

# Migrate database
python3 -m poetry install
python3 manage.py makemigrations
python3 manage.py migrate

# Create admin superuser
echo "from django.contrib.auth import \
      get_user_model; User = get_user_model(); \
      User.objects.create_superaccount(organization_slug='scalade', \
      email='admin@scalade.com', username='scalade', password='scalade', \
      is_business=True)" | python3 manage.py shell

echo "A development User has been created with:"
echo "organization_slug: scalade"
echo "email: admin@scalade.com"
echo "username: scalade"
echo "password: scalade"

# Create media directory
mkdir media
chmod -R 700 media
