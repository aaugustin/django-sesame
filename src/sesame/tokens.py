import logging

from django.contrib.auth import get_user_model
from django.core import signing
from django.utils import crypto
from django.utils.module_loading import import_string

from . import packers, settings

logger = logging.getLogger("sesame")


def get_signer():
    if settings.MAX_AGE is None:
        return signing.Signer(salt=settings.SALT)
    else:
        return signing.TimestampSigner(salt=settings.SALT)


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


def get_packer():
    if settings.PACKER is None:
        pk_type = get_user_model()._meta.pk.get_internal_type()
        try:
            Packer = packers.PACKERS[pk_type]
        except KeyError:
            raise NotImplementedError(pk_type + " primary keys aren't supported")
    else:
        Packer = import_string(settings.PACKER)
    return Packer()


packer = get_packer()


def get_revocation_key(user):
    """
    When the value returned by this method changes, this revocates tokens.

    It always includes the password so that changing the password revokes
    existing tokens.

    In addition, for one-time tokens, it also contains the last login
    datetime so that logging in revokes existing tokens.

    """
    value = ""
    if settings.INVALIDATE_ON_PASSWORD_CHANGE:
        value += user.password
    if settings.ONE_TIME:
        value += str(user.last_login)
    # The password is expected to be a secure hash but we hash it again
    # for additional safety. We default to MD5 to minimize the length of
    # the token. (Remember, if an attacker obtains the URL, he can already
    # log in. This isn't high security.)
    return crypto.pbkdf2(
        value, settings.SALT, settings.ITERATIONS, digest=settings.DIGEST,
    )


def create_token(user):
    """
    Create a signed token from a user.

    """
    pk = packer.pack_pk(user.pk)
    key = get_revocation_key(user)
    return sign(pk + key)


def parse_token(token, get_user):
    """
    Obtain a user from a signed token.

    """
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
            "Valid signature but unexpected token - if you changed "
            "django-sesame settings, you must regenerate tokens"
        )
        return

    pk, key = packer.unpack_pk(data)

    user = get_user(pk)
    if user is None:
        logger.debug("Unknown or inactive user: %s", pk)
        return
    if not crypto.constant_time_compare(key, get_revocation_key(user)):
        logger.debug("Invalid token: %s", token)
        return
    logger.debug("Valid token for user %s: %s", user, token)

    return user
