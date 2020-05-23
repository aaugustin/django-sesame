from django.contrib.auth import backends as auth_backends

from .tokens import parse_token


class SesameBackendMixin:
    """
    Authenticate with a django-sesame token.

    Mix this class in an authentication backend providing ``get_user(user_id)``.

    """

    def authenticate(self, request, sesame):
        """
        Check the token and return the corresponding user.

        """
        return parse_token(sesame, self.get_user)


class ModelBackend(SesameBackendMixin, auth_backends.ModelBackend):
    """
    Authenticate with a django-sesame token.

    """
