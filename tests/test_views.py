import http

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from sesame.utils import get_parameters

from .mixins import CreateUserMixin


class TestLoginView(CreateUserMixin, TestCase):
    def test_success(self):
        params = get_parameters(self.user)
        response = self.client.get("/login/", params)
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertRedirects(response, "/login/redirect/url/")

    def test_success_no_redirect(self):
        params = get_parameters(self.user)
        response = self.client.get("/login/no_redirect/", params)
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertEqual(response.status_code, http.HTTPStatus.NO_CONTENT)

    def test_failure_missing_token(self):
        response = self.client.get("/login/")
        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, http.HTTPStatus.FORBIDDEN)

    def test_failure_invalid_token(self):
        params = get_parameters(self.user)
        params["sesame"] = params["sesame"].lower()
        response = self.client.get("/login/", params)
        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, http.HTTPStatus.FORBIDDEN)

    @override_settings(
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
        ],
    )
    def test_without_auth_middleware(self):
        params = get_parameters(self.user)
        with self.assertRaises(ImproperlyConfigured) as exc:
            self.client.get("/login/", params)
        self.assertEqual(
            str(exc.exception),
            "LoginView requires django.contrib.auth",
        )
