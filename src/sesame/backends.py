from django.contrib.auth import backends as auth_backends
from django.contrib.auth import get_user_model

from . import settings
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
            return None
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

    def get_user(self, user_id):
        """
        Fetch user from the database by primary key.

        The field used by django-sesame as a primary key can be configured with
        the :data:`SESAME_PRIMARY_KEY_FIELD` setting.

        Return :obj:`None` if no active user is found.

        """
        User = get_user_model()
        try:
            user = User._default_manager.get(**{settings.PRIMARY_KEY_FIELD: user_id})
        except User.DoesNotExist:
            return None
        if self.user_can_authenticate(user):
            return user
        else:
            return None
