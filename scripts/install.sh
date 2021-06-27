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
      from common.utils import ModelManager; \
      account = User.objects.create_superaccount(organization_slug='scalade', \
      email='master@scalade.com', username='master', password='scalade'); \
      business = ModelManager.handle('accounts.business', 'create', \
      organization_name='Scalade', organization_slug='scalade', master_account=account);" \
      | python3 manage.py shell

echo "A development User has been created with:"
echo "organization_slug: scalade"
echo "email: master@scalade.com"
echo "username: scalade"
echo "password: scalade"

# Create media directory
mkdir media
chmod -R 700 media
