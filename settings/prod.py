# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '' # get it from environment variables

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'scalade',
        'USER': 'scaladeuser',
        'PASSWORD': 'scaladepass',
        'HOST': 'localhost',
        'PORT': 5432,
    },
}

SESSION_COOKIE_SECURE = True
