from urllib.parse import urlencode

from django.contrib.auth import authenticate
from django.utils import timezone

from . import settings
from .tokens import create_token as get_token

__all__ = ["get_token", "get_parameters", "get_query_string", "get_user"]


def get_parameters(user, scope=""):
    """
    Return GET parameters to authenticate a user.

    """
    return {settings.TOKEN_NAME: get_token(user, scope)}


def get_query_string(user, scope=""):
    """
    Return a complete query string to authenticate a user.

    """
    return "?" + urlencode(get_parameters(user, scope))


def get_user(request_or_sesame, update_last_login=None, scope="", max_age=None):
    """
    Authenticate a user based on a token.

    The first argument may be either a Django ``HttpRequest`` containing a
    token in the URL or the token itself, to support use cases outside the
    lifecycle of an HTTP request.

    If a valid token is found, return the user. Else, return None.

    If one-time tokens are enabled, update the last login date.

    """
    if isinstance(request_or_sesame, str):
        request = None
        sesame = request_or_sesame
    else:
        # request is expected to be a django.http.HttpRequest
        request = request_or_sesame
        try:
            sesame = request_or_sesame.GET.get(settings.TOKEN_NAME)
        except Exception:
            raise TypeError("get_user() expects a HttpRequest or a token")
        if sesame is None:
            return None

    user = authenticate(request, sesame=sesame, scope=scope, max_age=max_age)
    if user is None:
        return None

    if update_last_login is None:
        update_last_login = settings.ONE_TIME
    if update_last_login:
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

    return user
