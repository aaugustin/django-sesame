from __future__ import unicode_literals

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from .backends import UrlAuthBackendMixin
from .middleware import TOKEN_FIELD_NAME


def get_parameters(user):
    """
    Return GET parameters to log in `user`.

    """
    return {TOKEN_FIELD_NAME: UrlAuthBackendMixin().create_token(user)}


def get_query_string(user):
    """
    Return a complete query string to log in `user`.

    """
    return '?' + urlencode(get_parameters(user))
