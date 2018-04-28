from __future__ import unicode_literals

from .backends import UrlAuthBackendMixin
from .compat import urlencode
from .middleware import TOKEN_NAME


def get_parameters(user):
    """
    Return GET parameters to log in `user`.

    """
    return {TOKEN_NAME: UrlAuthBackendMixin().create_token(user)}


def get_query_string(user):
    """
    Return a complete query string to log in `user`.

    """
    return '?' + urlencode(get_parameters(user))
