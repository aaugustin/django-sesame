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
    required=True,
    permanent=False,
    override=True,
):
    """
    Decorator that looks for a signed token in the URL and authenticates a user.

    If a valid token is found, the user is available as ``request.user`` in the
    view. Else, :exc:`~django.core.exceptions.PermissionDenied` is raised,
    resulting in an HTTP 403 Forbidden error.

    :obj:`authenticate` may be applied to a view directly::

        @authenticate def view(request):
            ...

    or with arguments::

        @authenticate(scope="status-page")
        def view(request):
            ...

    If ``scope`` is set, a :ref:`scoped token <Scoped tokens>` is expected.

    If ``max_age`` is set, override the :data:`SESAME_MAX_AGE` setting.

    Set ``required`` to :obj:`False` to set ``request.user`` to an
    :class:`~django.contrib.auth.models.AnonymousUser` and execute the view when
    the token is invalid, instead of raising an exception. Then, you can check
    if ``request.user.is_authenticated``.

    :obj:`authenticate` doesn't log the user in permanently. It is intended to
    provide direct access to a specific resource without exposing all other
    private resources. This makes it more acceptable to use the less secure
    authentication mechanism provided by django-sesame.

    Set ``permanent`` to :obj:`True` to call :func:`~django.contrib.auth.login`
    after a user is authenticated.

    :obj:`authenticate` doesn't care if a user is already logged in. It looks
    for a signed token anyway and overrides ``request.user``.

    Set ``override`` to :obj:`False` to skip authentication if a user is already
    logged in.

    """
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
            scope=scope.format(*args, **kwargs),
            max_age=max_age,
        )

        request.user = user if user is not None else AnonymousUser()

        if required and user is None:
            raise PermissionDenied

        if permanent and user is not None:
            login(request, user)  # updates the last login date

        return view(request, *args, **kwargs)

    return wrapper
