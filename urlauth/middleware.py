from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser


TOKEN_FIELD_NAME = 'url_auth_token'


class AuthenticationMiddleware(object):

    def process_request(self, request):
        """Log user in if if `request` contains a valid login token."""
        token = request.GET.get(TOKEN_FIELD_NAME)
        if token is None:
            return
        user = authenticate(url_auth_token=token)
        if user is None:
            return

        # If the sessions framework is enabled and the token is valid,
        # persist the login in session.
        if hasattr(request, 'session') and user is not None:
            login(request, user)

        # If the authentication middleware isn't enabled, set request.user.
        # (This attribute is overwritten by the authentication middleware
        # if it runs after this one.)
        if not hasattr(request, 'user'):
            request.user = user if user is not None else AnonymousUser()
