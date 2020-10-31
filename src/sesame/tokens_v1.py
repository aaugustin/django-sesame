import logging
import re

import django
from django.core import signing
from django.utils import crypto

from . import packers, settings

__all__ = ["create_token", "detect_token", "parse_token"]

logger = logging.getLogger("sesame")


def get_revocation_key(user):
    """
    When the value returned by this method changes, this revocates tokens.

    It is derived from the hashed password so that changing the password
    revokes tokens.

    For one-time tokens, it also contains the last login datetime so that
    logging in revokes existing tokens.

    """
    data = ""
    if settings.INVALIDATE_ON_PASSWORD_CHANGE:
        data += user.password
    if settings.ONE_TIME:
        data += str(user.last_login)
    # The password is expected to be a secure hash but we hash it again
    # for additional safety. We default to MD5 to minimize the length of
    # the token. (Remember, if an attacker obtains the URL, he can already
    # log in. This isn't high security.)
    return crypto.pbkdf2(
        data,
        settings.SALT,
        settings.ITERATIONS,
        digest=settings.DIGEST,
    )


def get_signer():
    kwargs = {"salt": settings.SALT}
    if django.VERSION[:2] >= (3, 1):  # pragma: no cover
        kwargs["algorithm"] = "sha1"
    if settings.MAX_AGE is None:
        return signing.Signer(**kwargs)
    else:
        return signing.TimestampSigner(**kwargs)


signer = get_signer()


def sign(data):
    """
    Create an URL-safe, signed token from ``data``.

    """
    data = signing.b64_encode(data).decode()
    return signer.sign(data)


def unsign(token):
    """
    Extract the data from a signed ``token``.

    """
    if settings.MAX_AGE is None:
        data = signer.unsign(token)
    else:
        data = signer.unsign(token, max_age=settings.MAX_AGE)
    return signing.b64_decode(data.encode())


def create_token(user, scope=""):
    """
    Create a v1 signed token for a user.

    """
    if scope != "":
        raise NotImplementedError("v1 tokens don't support scope")
    primary_key = packers.packer.pack_pk(user.pk)
    key = get_revocation_key(user)
    return sign(primary_key + key)


def parse_token(token, get_user, scope=""):
    """
    Obtain a user from a v1 signed token.

    """
    if scope != "":
        raise NotImplementedError("v1 tokens don't support scope")
    try:
        data = unsign(token)
    except signing.SignatureExpired:
        logger.debug("Expired token: %s", token)
        return
    except signing.BadSignature:
        logger.debug("Bad token: %s", token)
        return
    except Exception:
        logger.exception(
            "Valid signature but unexpected token; if you enabled "
            "or disabled SESAME_MAX_AGE, you must regenerate tokens"
        )
        return

    try:
        user_pk, key = packers.packer.unpack_pk(data)
    except Exception:
        logger.exception(
            "Valid signature but unexpected token; if you changed "
            "SESAME_PACKER, you must regenerate tokens"
        )
        return

    user = get_user(user_pk)
    if user is None:
        logger.debug("Unknown or inactive user: %s", user_pk)
        return
    if not crypto.constant_time_compare(key, get_revocation_key(user)):
        logger.debug("Invalid token: %s", token)
        return
    logger.debug("Valid token for user %s: %s", user, token)

    return user


def get_token_re():
    if settings.MAX_AGE is None:
        # Size of primary key and revocation key depends on SESAME_PACKER and
        # SESAME_DIGEST. Default is 4 + 16 = 20 bytes = 27 Base64 characters.
        # Minimum "sensible" size is 1 + 2 = 3 bytes = 4 Base64 characters.
        return re.compile(r"[A-Za-z0-9-_]{4,}:[A-Za-z0-9-_]{27}")

    else:
        # All timestamps use 6 Base62 characters because 100000 in Base62 is
        # 1999-01-12T09:20:32Z, before django-sesame existed.
        return re.compile(r"[A-Za-z0-9-_]{4,}:[0-9A-Za-z]{6}:[A-Za-z0-9-_]{27}")


token_re = get_token_re()


def detect_token(token):
    """
    Tell whether token may be a v1 signed token.

    """
    return token_re.fullmatch(token) is not None
