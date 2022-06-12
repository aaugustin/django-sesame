from django.contrib.auth import backends as auth_backends

from .tokens import parse_token

__all__ = ["ModelBackend", "SesameBackendMixin"]


class SesameBackendMixin:
    """
    Mix this class in an authentication backend providing ``get_user(user_id)``
    to create an authentication backend usable with django-sesame.

    """

    def authenticate(self, request, sesame, scope="", max_age=None):
        """
        If ``sesame`` is a valid token, return the user. Else, return :obj:`None`.

        If ``scope`` is set, a :ref:`scoped token <Scoped tokens>` is expected.

        If ``max_age`` is set, override the :data:`SESAME_MAX_AGE` setting.

        ``request`` is an :class:`~django.http.HttpRequest` or :obj:`None`.

        """
        # This check shouldn't be necessary, but it can avoid problems like
        # issue #37 and Django's built-in backends include similar checks.
        if sesame is None:
            return
        return parse_token(sesame, self.get_user, scope, max_age)


class ModelBackend(SesameBackendMixin, auth_backends.ModelBackend):
    """
    Authentication backend that authenticates users with django-sesame tokens.

    It inherits :class:`SesameBackendMixin` and Django's built-in
    :class:`~django.contrib.auth.backends.ModelBackend`.

    Extending the default value of the :setting:`AUTHENTICATION_BACKENDS` setting
    to add  ``"sesame.backends.ModelBackend"`` looks like:

    .. code-block:: python

        AUTHENTICATION_BACKENDS = [
            "django.contrib.auth.backends.ModelBackend",
            "sesame.backends.ModelBackend",
        ]

    """
