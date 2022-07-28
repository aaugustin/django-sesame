import datetime
import hashlib
import importlib
import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEFAULTS = {
    # Generating URLs
    "TOKEN_NAME": "sesame",
    # Tokens lifecycle
    "MAX_AGE": None,
    "ONE_TIME": False,
    "INVALIDATE_ON_PASSWORD_CHANGE": True,
    # Custom primary keys
    "PACKER": None,
    "PRIMARY_KEY_FIELD": "pk",
    # Tokens
    "TOKENS": ["sesame.tokens_v2", "sesame.tokens_v1"],
    # Tokens v2
    "KEY": "",
    # We want a short signature in order to keep tokens short. A 10-bytes
    # signature has about 1.2e24 possible values, which is sufficient here.
    "SIGNATURE_SIZE": 10,
    # Tokens v1
    "SALT": "sesame",
    # These parameters aren't updated anymore. Tokens v2 are recommended.
    "DIGEST": hashlib.md5,
    "ITERATIONS": 10000,
}

__all__ = list(DEFAULTS)


# load() also works for reloading settings, which is useful for testing.


def load():
    module = sys.modules[__name__]
    for name, default in DEFAULTS.items():
        setattr(module, name, getattr(settings, "SESAME_" + name, default))

    global KEY, MAX_AGE, PACKER, PRIMARY_KEY_FIELD, TOKENS

    # Support defining MAX_AGE as a timedelta rather than a number of seconds.
    if isinstance(MAX_AGE, datetime.timedelta):
        MAX_AGE = MAX_AGE.total_seconds()

    # Import token creation and parsing modules.
    TOKENS = [importlib.import_module(tokens) for tokens in TOKENS]

    # Derive a personalized 64-bytes key from the base SECRET_KEY.
    # Include settings in the personalized key to invalidate tokens when
    # these settings change. This ensures that tokens generated with one
    # packer cannot be misinterpreted by another packer or that changing
    # MAX_AGE doesn't revive expired tokens, for example.
    base_key = "|".join(
        [
            # Usually SECRET_KEY is a str but Django also supports bytes.
            str(settings.SECRET_KEY),
            # For consistency, treat KEY like SECRET_KEY.
            str(KEY),
            # Changing MAX_AGE is allowed as long as it is not None.
            "max_age" if MAX_AGE is not None else "",
            PACKER if PACKER is not None else "",
            PRIMARY_KEY_FIELD,
        ]
    ).encode()
    KEY = hashlib.blake2b(base_key, person=b"sesame.settings").digest()


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
            "insecure configuration: set SESAME_MAX_AGE to a low value "
            "or set SESAME_INVALIDATE_ON_PASSWORD_CHANGE to True"
        )


check()
