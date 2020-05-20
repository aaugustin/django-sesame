from urllib.parse import urlencode

from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect

from . import settings
from .utils import get_user


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
        # If django.contrib.sessions is enabled, don't update the last login,
        # because login(request, user) will do it.
        # If django.contrib.sessions is dilabled, keep the default behavior of
        # updating last login only for one-time tokens.
        update_last_login = False if hasattr(request, "session") else None

        user = get_user(request, update_last_login)

        # If django.contrib.sessions is enabled and the token is valid,
        # persist the login in session.
        if hasattr(request, "session") and user is not None:
            login(request, user)
            # Once we persist the login in the session, if the authentication
            # middleware is enabled, it will set request.user in future
            # requests. We can get rid of the token in the URL by redirecting
            # to the same URL with the token removed. We only do this for GET
            # requests because redirecting POST requests doesn't work well. We
            # don't do this on Safari because it triggers the over-zealous
            # "Protection Against First Party Bounce Trackers" of ITP 2.0.
            if (
                hasattr(request, "user")
                and request.method == "GET"
                and not self.is_safari(request)
            ):
                return self.get_redirect(request)

        # If django.contrib.auth isn't enabled, set request.user.
        if not hasattr(request, "user"):
            request.user = user if user is not None else AnonymousUser()

    @staticmethod
    def is_safari(request):
        try:
            from ua_parser import user_agent_parser
        except ImportError:  # pragma: no cover
            return None
        else:
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            parsed_ua = user_agent_parser.Parse(user_agent)
            return (
                parsed_ua["user_agent"]["family"] == "Safari"
                or parsed_ua["os"]["family"] == "iOS"
            )

    @staticmethod
    def get_redirect(request):
        """
        Create a HTTP redirect response that removes the token from the URL.

        """
        params = request.GET.copy()
        params.pop(settings.TOKEN_NAME)
        url = request.path
        if params:
            url += "?" + urlencode(params)
        return redirect(url)
