from __future__ import unicode_literals

import hashlib
import logging

from django.conf import settings
from django.contrib.auth import backends as auth_backends
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.utils import crypto
from django.utils.functional import cached_property

from . import packers

logger = logging.getLogger("sesame")


class UrlAuthBackendMixin(object):
    """
    Tools to authenticate against a token containing a signed user id.

    Mix this class in an auth backend providing ``get_user(user_id)`` and call
    ``parse_token(token)`` from its ``authenticate(**credentials)``.

    """

    salt = getattr(settings, "SESAME_SALT", "sesame")
    digest = getattr(settings, "SESAME_DIGEST", hashlib.md5)
    iterations = getattr(settings, "SESAME_ITERATIONS", 10000)

    max_age = getattr(settings, "SESAME_MAX_AGE", None)
    one_time = getattr(settings, "SESAME_ONE_TIME", False)
    invalidate_on_password_change = getattr(
        settings, "SESAME_INVALIDATE_ON_PASSWORD_CHANGE", True
    )

    def __init__(self, *args, **kwargs):
        if self.max_age is None and not self.invalidate_on_password_change:
            raise ImproperlyConfigured(
                "Insecure configuration: set SESAME_MAX_AGE to a low value "
                "or set SESAME_INVALIDATE_ON_PASSWORD_CHANGE to True"
            )
        super(UrlAuthBackendMixin, self).__init__(*args, **kwargs)

    @cached_property
    def signer(self):
        if self.max_age is None:
            return signing.Signer(salt=self.salt)
        else:
            return signing.TimestampSigner(salt=self.salt)

    def sign(self, data):
        """
        Create an URL-safe, signed token from ``data``.

        """
        data = signing.b64_encode(data).decode()
        return self.signer.sign(data)

    def unsign(self, token):
        """
        Extract the data from a signed ``token``.

        """
        if self.max_age is None:
            data = self.signer.unsign(token)
        else:
            data = self.signer.unsign(token, max_age=self.max_age)
        return signing.b64_decode(data.encode())

    @cached_property
    def packer(self):
        pk_type = get_user_model()._meta.pk.get_internal_type()
        try:
            Packer = packers.PACKERS[pk_type]
        except KeyError:
            raise NotImplementedError(
                pk_type + " primary keys aren't supported at this time"
            )
        return Packer()

    def get_revocation_key(self, user):
        """
        When the value returned by this method changes, this revocates tokens.

        It always includes the password so that changing the password revokes
        existing tokens.

        In addition, for one-time tokens, it also contains the last login
        datetime so that logging in revokes existing tokens.

        """
        value = ""
        if self.invalidate_on_password_change:
            value += user.password
        if self.one_time:
            value += str(user.last_login)
        return value

    def create_token(self, user):
        """
        Create a signed token from a user.

        """
        # The password is expected to be a secure hash but we hash it again
        # for additional safety. We default to MD5 to minimize the length of
        # the token. (Remember, if an attacker obtains the URL, he can already
        # log in. This isn't high security.)
        h = crypto.pbkdf2(
            self.get_revocation_key(user),
            self.salt,
            self.iterations,
            digest=self.digest,
        )
        return self.sign(self.packer.pack_pk(user.pk) + h)

    def parse_token(self, token):
        """
        Obtain a user from a signed token.

        """
        try:
            data = self.unsign(token)
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
        user_pk, data = self.packer.unpack_pk(data)
        user = self.get_user(user_pk)
        if user is None:
            logger.debug("Unknown or inactive user: %s", user_pk)
            return
        h = crypto.pbkdf2(
            self.get_revocation_key(user),
            self.salt,
            self.iterations,
            digest=self.digest,
        )
        if not crypto.constant_time_compare(data, h):
            logger.debug("Invalid token: %s", token)
            return
        logger.debug("Valid token for user %s: %s", user, token)
        return user

    def authenticate(self, request, url_auth_token=None):
        """
        Check the token and return the corresponding user.

        """
        try:
            return self.parse_token(url_auth_token)
        except TypeError:
            backend = "%s.%s" % (self.__module__, self.__class__.__name__)
            logger.exception(
                "TypeError in %s, here's the traceback before Django swallows it:",
                backend,
            )
            raise


class ModelBackend(UrlAuthBackendMixin, auth_backends.ModelBackend):
    """
    Authenticates against a token containing a signed user id.

    """
