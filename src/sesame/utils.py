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


def get_user(request, update_last_login=None, scope=""):
    """
    Authenticate a user based on the token found in the URL.

    If a valid token is found and one-time tokens are enabled,
    update the last login date and return the user.

    Else, return None.

    """
    token = request.GET.get(settings.TOKEN_NAME)
    if token is None:
        return None

    user = authenticate(request, sesame=token, scope=scope)
    if user is None:
        return None

    if update_last_login is None:
        update_last_login = settings.ONE_TIME
    if update_last_login:
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

    return user
