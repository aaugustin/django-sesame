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
        self._redirect_url = None

    def __call__(self, request):
        self._redirect_url = None
        self.process_request(request)
        response = self.get_response(request)

        if self._redirect_url:
            redirect_response = redirect(self._redirect_url)
            redirect_response.content = response.content
            return redirect_response

        return response

    def process_request(self, request):
        """
        Log user in if `request` contains a valid login token.
        """
        token = request.GET.get(TOKEN_NAME)
        if token is None:
            return

        user = authenticate(url_auth_token=token)
        if user is None:
            return

        # If the sessions framework is enabled and the token is valid,
        # persist the login in session.
        if hasattr(request, 'session') and user is not None:
            login(request, user)
            self._set_redirect_url(request)

        # If the authentication middleware isn't enabled, set request.user.
        # (This attribute is overwritten by the authentication middleware
        # if it runs after this one.)
        if not hasattr(request, 'user'):
            request.user = user if user is not None else AnonymousUser()

    def _set_redirect_url(self, request):
        params = request.GET.copy()
        params.pop(TOKEN_NAME)
        url = request.path + ('?' + urlencode(params) if params else '')
        self._redirect_url = url
