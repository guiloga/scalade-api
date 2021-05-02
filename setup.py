import os
import django


def django_apps_setup():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    django.setup()
