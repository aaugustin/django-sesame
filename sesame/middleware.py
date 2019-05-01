from __future__ import unicode_literals

from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect

from .compatibility import urlencode
from .utils import TOKEN_NAME, get_user


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
        user = get_user(request)

        # If the sessions framework is enabled and the token is valid,
        # persist the login in session.
        if hasattr(request, 'session') and user is not None:
            login(request, user)
            # Once we persist the login in the session, if the authentication
            # middleware is enabled, it will set request.user in future
            # requests. We can get rid of the token in the URL by redirecting
            # to the same URL with the token removed. We only do this for GET
            # requests because redirecting POST requests doesn't work well. We
            # don't do this on Safari because it triggers the over-zealous
            # "Protection Against First Party Bounce Trackers" of ITP 2.0.
            if (
                hasattr(request, 'user') and
                request.method == 'GET' and
                not self.is_safari(request)
            ):
                return self.get_redirect(request)

        # If the authentication middleware isn't enabled, set request.user.
        # (This attribute is overwritten by the authentication middleware
        # if it runs after this one.)
        if not hasattr(request, 'user'):
            request.user = user if user is not None else AnonymousUser()

    @staticmethod
    def is_safari(request):
        try:
            from ua_parser import user_agent_parser
        except ImportError:                                 # pragma: no cover
            return None
        else:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            browser = user_agent_parser.ParseUserAgent(user_agent)['family']
            return browser == 'Safari'

    @staticmethod
    def get_redirect(request):
        """
        Create a HTTP redirect response that removes the token from the URL.

        """
        params = request.GET.copy()
        params.pop(TOKEN_NAME)
        url = request.path
        if params:
            url += '?' + urlencode(params)
        return redirect(url)
