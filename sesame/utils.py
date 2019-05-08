from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate

from .backends import UrlAuthBackendMixin
from .compatibility import urlencode

TOKEN_NAME = getattr(settings, "SESAME_TOKEN_NAME", "url_auth_token")


def get_parameters(user):
    """
    Return GET parameters to log in `user`.

    """
    return {TOKEN_NAME: UrlAuthBackendMixin().create_token(user)}


def get_query_string(user):
    """
    Return a complete query string to log in `user`.

    """
    return "?" + urlencode(get_parameters(user))


def get_user(request):
    """
    Authenticate a user based on the token found in the URL.

    Return None if no valid token is found.

    """
    url_auth_token = request.GET.get(TOKEN_NAME)
    if url_auth_token is None:
        return None

    return authenticate(url_auth_token=url_auth_token)
