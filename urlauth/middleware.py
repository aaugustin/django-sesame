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

        if hasattr(request, 'session'):
            # If the sessions framework is enabled and the token is valid,
            # persist the login in session and let django.contrib.auth's
            # middleware do the rest.
            if user is not None:
                login(request, user)
        else:
            # If the sessions framework isn't enabled, django.contrib.auth's
            # middleware isn't either, so we have to create request.user.
            request.user = user if user is not None else AnonymousUser()
