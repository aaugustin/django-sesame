import http

from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from sesame.utils import get_parameters

from .mixins import CreateUserMixin


class TestAuthenticate(CreateUserMixin, TestCase):
    def test_success(self):
        params = get_parameters(self.user)
        response = self.client.get("/authenticate/", params)
        # User is logged in with django.contrib.auth.
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertContains(response, self.user.username)

    def test_default_required(self):
        response = self.client.get("/authenticate/")
        # User isn't logged in with django.contrib.auth.
        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, http.HTTPStatus.FORBIDDEN)

    def test_not_required(self):
        response = self.client.get("/authenticate/not_required/")
        # User isn't logged in with django.contrib.auth.
        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertContains(response, "anonymous")

    def test_default_not_permanent(self):
        params = get_parameters(self.user)
        response = self.client.get("/authenticate/", params)
        # User isn't logged in with django.contrib.sessions
        self.assertIsInstance(get_user(response.wsgi_request), AnonymousUser)
        self.assertContains(response, self.user.username)

    def test_permanent(self):
        params = get_parameters(self.user)
        response = self.client.get("/authenticate/permanent/", params)
        # User is logged in with django.contrib.sessions.
        self.assertEqual(get_user(response.wsgi_request), self.user)
        self.assertContains(response, self.user.username)

    def test_default_override(self):
        user1 = self.user
        user2 = self.create_user("jane")
        self.client.force_login(user1)
        params = get_parameters(user2)
        response = self.client.get("/authenticate/", params)
        self.assertEqual(response.wsgi_request.user, user2)
        self.assertContains(response, user2.username)

    def test_no_override(self):
        user1 = self.user
        user2 = self.create_user("jane")
        self.client.force_login(user1)
        params = get_parameters(user2)
        response = self.client.get("/authenticate/no_override/", params)
        self.assertEqual(response.wsgi_request.user, user1)
        self.assertContains(response, user1.username)

    @override_settings(MIDDLEWARE=[])
    def test_without_session_middleware(self):
        params = get_parameters(self.user)
        response = self.client.get("/authenticate/", params)
        self.assertContains(response, self.user.username)

    @override_settings(MIDDLEWARE=[])
    def test_permanent_without_session_middleware(self):
        params = get_parameters(self.user)
        with self.assertRaises(ImproperlyConfigured) as exc:
            self.client.get("/authenticate/permanent/", params)
        self.assertEqual(
            str(exc.exception),
            "authenticate(permanent=True) requires django.contrib.sessions",
        )
