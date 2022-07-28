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


def derive_key(secret_key, key):
    """
    Make a 64-bytes key from Django's ``secret_key`` and django-sesame's ``key``.

    Include settings in the key to invalidate tokens when these settings change.
    This ensures that tokens generated with one packer cannot be misinterpreted
    by another packer, for example.

    """
    global MAX_AGE, PACKER, PRIMARY_KEY_FIELD
    return hashlib.blake2b(
        "|".join(
            [
                # Usually a str but Django also supports bytes.
                str(secret_key),
                # Treat key like secret_key for consistency.
                str(key),
                # Changing MAX_AGE is allowed as long as it is not None.
                "max_age" if MAX_AGE is not None else "",
                PACKER if PACKER is not None else "",
                PRIMARY_KEY_FIELD,
            ]
        ).encode(),
        person=b"sesame.settings",
    ).digest()


# load() also works for reloading settings, which is useful for testing.


def load():
    module = sys.modules[__name__]
    for name, default in DEFAULTS.items():
        setattr(module, name, getattr(settings, "SESAME_" + name, default))

    global KEY, MAX_AGE, SIGNING_KEY, TOKENS, VERIFICATION_KEYS

    # Support defining MAX_AGE as a timedelta rather than a number of seconds.
    if isinstance(MAX_AGE, datetime.timedelta):
        MAX_AGE = MAX_AGE.total_seconds()

    # Import token creation and parsing modules.
    TOKENS = [importlib.import_module(tokens) for tokens in TOKENS]

    # Derive signing and verification keys.
    SIGNING_KEY = derive_key(settings.SECRET_KEY, KEY)
    VERIFICATION_KEYS = [SIGNING_KEY] + [
        derive_key(secret_key, KEY)
        for secret_key in getattr(settings, "SECRET_KEY_FALLBACKS", [])
    ]


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
