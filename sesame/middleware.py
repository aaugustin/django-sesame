from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect

from .compat import urlencode

TOKEN_NAME = getattr(settings, 'SESAME_TOKEN_NAME', 'url_auth_token')


class AuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.process_request(request):
            return self.get_redirect(request)
        else:
            return self.get_response(request)

    def process_request(self, request):
        """
        Log user in if `request` contains a valid login token.
        """
        token = request.GET.get(TOKEN_NAME)
        if token is None:
            return False

        user = authenticate(url_auth_token=token)
        if user is None:
            return False

        # If the sessions framework is enabled and the token is valid,
        # persist the login in session.
        if hasattr(request, 'session') and user is not None:
            login(request, user)
            return True

        # If the authentication middleware isn't enabled, set request.user.
        # (This attribute is overwritten by the authentication middleware
        # if it runs after this one.)
        if not hasattr(request, 'user'):
            request.user = user if user is not None else AnonymousUser()
            return False

        return False

    def get_redirect(self, request):
        """
        Get redirect response with the token removed.
        """
        params = request.GET.copy()
        params.pop(TOKEN_NAME)
        url = request.path + ('?' + urlencode(params) if params else '')
        return redirect(url)
