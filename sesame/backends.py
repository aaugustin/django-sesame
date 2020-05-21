import logging

from django.contrib.auth import backends as auth_backends
from django.contrib.auth import get_user_model
from django.core import signing
from django.utils import crypto
from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from . import packers, settings

logger = logging.getLogger("sesame")


class UrlAuthBackendMixin:
    """
    Tools to authenticate against a token containing a signed user id.

    Mix this class in an auth backend providing ``get_user(user_id)`` and call
    ``parse_token(token)`` from its ``authenticate(**credentials)``.

    """

    @cached_property
    def signer(self):
        if settings.MAX_AGE is None:
            return signing.Signer(salt=settings.SALT)
        else:
            return signing.TimestampSigner(salt=settings.SALT)

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
        if settings.MAX_AGE is None:
            data = self.signer.unsign(token)
        else:
            data = self.signer.unsign(token, max_age=settings.MAX_AGE)
        return signing.b64_decode(data.encode())

    @cached_property
    def packer(self):
        if settings.PACKER is None:
            pk_type = get_user_model()._meta.pk.get_internal_type()
            try:
                Packer = packers.PACKERS[pk_type]
            except KeyError:
                raise NotImplementedError(pk_type + " primary keys aren't supported")
        else:
            Packer = import_string(settings.PACKER)
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

    def create_token(self, user):
        """
        Create a signed token from a user.

        """
        pk = self.packer.pack_pk(user.pk)
        key = self.get_revocation_key(user)
        return self.sign(pk + key)

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

        pk, key = self.packer.unpack_pk(data)

        user = self.get_user(pk)
        if user is None:
            logger.debug("Unknown or inactive user: %s", pk)
            return
        if not crypto.constant_time_compare(key, self.get_revocation_key(user)):
            logger.debug("Invalid token: %s", token)
            return
        logger.debug("Valid token for user %s: %s", user, token)

        return user

    def authenticate(self, request, url_auth_token):
        """
        Check the token and return the corresponding user.

        """
        return self.parse_token(url_auth_token)


class ModelBackend(UrlAuthBackendMixin, auth_backends.ModelBackend):
    """
    Authenticates against a token containing a signed user id.

    """
