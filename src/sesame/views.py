from http import HTTPStatus

from django.conf import settings as django_settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.http import url_has_allowed_host_and_scheme  # private API
from django.views.generic import View

from . import settings

try:
    from django.contrib.auth.views import RedirectURLMixin  # private API
except ImportError:  # Django < 4.1
    # Added to Django in https://github.com/django/django/pull/15608
    class RedirectURLMixin:
        next_page = None
        redirect_field_name = REDIRECT_FIELD_NAME
        success_url_allowed_hosts = set()

        def get_success_url(self):
            return self.get_redirect_url() or self.get_default_redirect_url()

        def get_redirect_url(self):
            """Return the user-originating redirect URL if it's safe."""
            redirect_to = self.request.POST.get(
                self.redirect_field_name, self.request.GET.get(self.redirect_field_name)
            )
            url_is_safe = url_has_allowed_host_and_scheme(
                url=redirect_to,
                allowed_hosts=self.get_success_url_allowed_hosts(),
                require_https=self.request.is_secure(),
            )
            return redirect_to if url_is_safe else ""

        def get_success_url_allowed_hosts(self):
            return {self.request.get_host(), *self.success_url_allowed_hosts}

        def get_default_redirect_url(self):
            """Return the default redirect URL."""
            if self.next_page:
                return resolve_url(self.next_page)
            else:  # pragma: no cover
                raise ImproperlyConfigured(
                    "No URL to redirect to. Provide a next_page."
                )


__all__ = ["LoginView"]


class LoginView(RedirectURLMixin, View):

    scope = ""
    max_age = None
    next_page = django_settings.LOGIN_REDIRECT_URL

    def get(self, request):
        if not hasattr(request, "user"):
            raise ImproperlyConfigured("LoginView requires django.contrib.auth")

        sesame = request.GET.get(settings.TOKEN_NAME)
        if sesame is None:
            raise PermissionDenied

        user = authenticate(
            request,
            sesame=sesame,
            scope=self.scope,
            max_age=self.max_age,
        )
        if user is None:
            raise PermissionDenied

        login(request, user)  # updates the last login date

        if self.next_page is None:
            return HttpResponse(status=HTTPStatus.NO_CONTENT)
        else:
            return HttpResponseRedirect(self.get_success_url())
