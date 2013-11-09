from __future__ import unicode_literals

CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
}

DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3'},
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'sesame',
)

LOGGING_CONFIG = None

ROOT_URLCONF = 'sesame.test_urls'

SECRET_KEY = 'Anyone who finds an URL will be able to log in. Seriously.'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
