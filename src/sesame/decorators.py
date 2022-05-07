import functools

from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from .utils import get_user

__all__ = ["authenticate"]


def authenticate(
    view=None,
    *,
    scope="",
    max_age=None,
    required=False,
    permanent=False,
    override=True,
):
    if view is None:
        return functools.partial(
            authenticate,
            scope=scope,
            max_age=max_age,
            required=required,
            permanent=permanent,
            override=override,
        )

    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        # Skip when a user is already logged in, unless override is enabled.
        if hasattr(request, "user") and request.user.is_authenticated and not override:
            return view(request, *args, **kwargs)

        if permanent and not hasattr(request, "session"):
            raise ImproperlyConfigured(
                "authenticate(permanent=True) requires django.contrib.sessions"
            )
        # If the user will be logged in, don't update the last login, because
        # login(request, user) will do it. Else, keep the default behavior of
        # updating last login only for one-time tokens.
        user = get_user(
            request,
            update_last_login=False if permanent else None,
            scope=scope,
            max_age=max_age,
        )

        request.user = user if user is not None else AnonymousUser()

        if required and user is None:
            raise PermissionDenied

        if permanent and user is not None:
            login(request, user)  # updates the last login date

        return view(request, *args, **kwargs)

    return wrapper
