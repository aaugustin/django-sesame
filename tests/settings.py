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
    "tests",
]

LOGIN_REDIRECT_URL = "/login/redirect/url/"

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

ROOT_URLCONF = "tests.urls"

SECRET_KEY = "Anyone who finds a URL will be able to log in. Seriously."

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "context_processors": ["django.contrib.auth.context_processors.auth"]
        },
    }
]

USE_TZ = True
