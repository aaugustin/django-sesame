from django.contrib.auth import backends as auth_backends

from .tokens import parse_token


class UrlAuthBackendMixin:
    """
    Authenticate with a token containing a signed user id.

    Mix this class in an authentication backend providing ``get_user(user_id)``.

    """

    def authenticate(self, request, url_auth_token):
        """
        Check the token and return the corresponding user.

        """
        return parse_token(url_auth_token, self.get_user)


class ModelBackend(UrlAuthBackendMixin, auth_backends.ModelBackend):
    """
    Authenticates against a token containing a signed user id.

    """
