from .common import *

ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

if ENVIRONMENT == 'prod':
    from .prod import *
else:
    from .dev import *

if ENVIRONMENT == 'dev':
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE

USE_TEST_DB = os.getenv('USE_TEST_DATABASE', False) == 'True'

if USE_TEST_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'test_scalade',
            'USER': 'scaladeuser',
            'PASSWORD': 'scaladepass',
            'HOST': 'localhost',
            'PORT': 5433,
        },
    }
