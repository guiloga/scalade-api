DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '192.168.1.225',
    'scalade.io',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'scalade',
        'USER': 'scaladeuser',
        'PASSWORD': 'scaladepass',
        'HOST': 'localhost',
        'PORT': 5433,
    },
}
