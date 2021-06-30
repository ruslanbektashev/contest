from .common_settings import *

SECRET_KEY = '^*ul90n!wc1xhcui@^55!)4y0)eew6*u!@%l(7iv-33p-$$wfe'

DEBUG = True

ALLOWED_HOSTS = ['localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'contest',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
