from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect

from .compatibility import urlencode

TOKEN_NAME = getattr(settings, 'SESAME_TOKEN_NAME', 'url_auth_token')


class AuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # When process_request() returns a response, return that response.
        # Otherwise continue with the next middleware or the view.
        return self.process_request(request) or self.get_response(request)

    def process_request(self, request):
        """
        Log user in if `request` contains a valid login token.

        Return a HTTP redirect response that removes the token from the URL
        after a successful login when sessions are enabled, else ``None``.

        """
        token = request.GET.get(TOKEN_NAME)
        user = None if token is None else authenticate(url_auth_token=token)

        # If the sessions framework is enabled and the token is valid,
        # persist the login in session.
        if hasattr(request, 'session') and user is not None:
            login(request, user)
            # Once we persist the login in the session, if the authentication
            # middleware is enabled, it will set request.user in future
            # requests. We can get rid of the token in the URL by redirecting
            # to the same URL with the token removed. We only do this for GET
            # requests because redirecting POST requests doesn't work well.
            if hasattr(request, 'user') and request.method == 'GET':
                return self.get_redirect(request)

        # If the authentication middleware isn't enabled, set request.user.
        # (This attribute is overwritten by the authentication middleware
        # if it runs after this one.)
        if not hasattr(request, 'user'):
            request.user = user if user is not None else AnonymousUser()

    def get_redirect(self, request):
        """
        Create a HTTP redirect response that removes the token from the URL.

        """
        params = request.GET.copy()
        params.pop(TOKEN_NAME)
        url = request.path
        if params:
            url += '?' + urlencode(params)
        return redirect(url)
