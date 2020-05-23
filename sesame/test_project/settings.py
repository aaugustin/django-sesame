# Include the sesame backend first to avoid bogus database queries caused by
# https://code.djangoproject.com/ticket/30556 and simplify assertNumQueries.

AUTHENTICATION_BACKENDS = [
    "sesame.backends.ModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "sesame",
    "sesame.test_app",
]

LOGGING_CONFIG = None

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

PASSWORD_HASHERS = ["django.contrib.auth.hashers.SHA1PasswordHasher"]

ROOT_URLCONF = "sesame.test_urls"

SECRET_KEY = "Anyone who finds a URL will be able to log in. Seriously."

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates"}]
