#!/bin/sh

# migrate database
python manage.py makemigrations
python manage.py migrate

# create superuser
echo "from django.contrib.auth import \
      get_user_model; User = get_user_model(); \
      User.objects.create_superaccount(organization_slug='scalade', \
      email='admin@scalade.com', username='scalade', password='scalade', \
      is_business=True)" | python manage.py shell

echo "A development User has been created with:"
echo "organization_slug: scalade"
echo "email: admin@scalade.com"
echo "username: scalade"
echo "password: scalade"


python manage.py accounts_add workspace "{\"name\": \"default\"}"

mkdir media
chmod -R 777 media