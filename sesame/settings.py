import hashlib
import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEFAULTS = {
    # Generating URLs
    "TOKEN_NAME": "url_auth_token",
    # Tokens lifecycle
    "MAX_AGE": None,
    "ONE_TIME": False,
    "INVALIDATE_ON_PASSWORD_CHANGE": True,
    # Custom primary keys
    "PACKER": None,
    # Tokens security
    "SALT": "sesame",
    "DIGEST": hashlib.md5,
    "ITERATIONS": 10000,
}


# load() also works for reloading settings, which is useful for testing.


def load():
    module = sys.modules[__name__]
    for name, default in DEFAULTS.items():
        setattr(module, name, getattr(settings, "SESAME_" + name, default))


load()


# Django's checks framework was designed to run such checks. Unfortunately,
# there's no way to guarantee that a check would be discovered, because
# django-sesame never required adding the "sesame" app to INSTALLED_APPS.

# The benefits of writing this check with the checks framework don't justify
# adding another step to the installation instructions. Raising an exception
# is good enough.


def check():
    global MAX_AGE, INVALIDATE_ON_PASSWORD_CHANGE
    if MAX_AGE is None and not INVALIDATE_ON_PASSWORD_CHANGE:
        raise ImproperlyConfigured(
            "Insecure configuration: set SESAME_MAX_AGE to a low value "
            "or set SESAME_INVALIDATE_ON_PASSWORD_CHANGE to True"
        )


check()
