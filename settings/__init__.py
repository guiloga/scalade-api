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
