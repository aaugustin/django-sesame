from urllib.parse import urlencode

from django.contrib.auth import authenticate
from django.utils import timezone

from . import settings, tokens_v1


def get_parameters(user):
    """
    Return GET parameters to log in `user`.

    """
    return {settings.TOKEN_NAME: tokens_v1.create_token(user)}


def get_query_string(user):
    """
    Return a complete query string to log in `user`.

    """
    return "?" + urlencode(get_parameters(user))


def get_user(request, update_last_login=None):
    """
    Authenticate a user based on the token found in the URL.

    If a valid token is found, update the last login date and return the user.

    Else, return None.

    """
    token = request.GET.get(settings.TOKEN_NAME)
    if token is None:
        return None

    user = authenticate(request, sesame=token)
    if user is None:
        return None

    if update_last_login is None:
        update_last_login = settings.ONE_TIME
    if update_last_login:
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

    return user
