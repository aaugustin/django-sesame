import hashlib
import logging
import struct

from django.contrib.auth import backends as auth_backends
from django.core import signing
from django.utils import crypto


logger = logging.getLogger('sesame')


class UrlAuthBackendMixin(object):
    """Tools to authenticate against a token containing a signed user id.

    Mix this class in an authentication backend providing `get_user(user_id)`,
    and call `parse_token(token)` from its `authenticate(**credentials)`.
    """

    signer = signing.Signer(salt='sesame')

    def sign(self, data):
        """Create an URL-safe, signed token from `data`."""
        return self.signer.sign(unicode(signing.b64_encode(data), 'ascii'))

    def unsign(self, token):
        """Extract the data from a signed `token`."""
        return signing.b64_decode(self.signer.unsign(token).encode('ascii'))

    def create_token(self, user):
        """Create a signed token from an `auth.User`."""
        # Include a hash derived from the password so changing the password
        # revokes the token. Usually, user.password will be a secure hash
        # already, but we hash it again in case it isn't. We use MD5
        # to minimize the length of the token. (Remember, if an attacker
        # obtains the URL, he can already log in. This isn't high security.)
        h = crypto.pbkdf2(user.password, 'sesame', 10000, digest=hashlib.md5)
        return self.sign(struct.pack('!i', user.pk) + h)

    def parse_token(self, token):
        """Obtain an `auth.User` from a signed token."""
        try:
            data = self.unsign(token)
        except signing.BadSignature:
            logger.debug(u"Invalid token: %s", token)
            return
        user = self.get_user(*struct.unpack('!i', data[:4]))
        if user is None:
            logger.debug(u"Unknown token: %s", token)
            return
        h = crypto.pbkdf2(user.password, 'sesame', 10000, digest=hashlib.md5)
        if not crypto.constant_time_compare(data[4:], h):
            logger.debug(u"Expired token: %s", token)
            return
        logger.debug(u"Valid token for user %s: %s", user, token)
        return user


class ModelBackend(UrlAuthBackendMixin, auth_backends.ModelBackend):
    """Authenticates against a token containing a signed user id."""

    def authenticate(self, url_auth_token=None):
        """Check the token and return an `auth.User`."""
        try:
            return self.parse_token(url_auth_token)
        except TypeError:
            backend = u"%s.%s" % (self.__module__, self.__class__.__name__)
            logger.exception(u"TypeError in %s, here's the traceback before "
                             u"Django swallows it:", backend)
            raise
