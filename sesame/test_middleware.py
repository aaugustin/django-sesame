from __future__ import unicode_literals

import io
import logging
import unittest

from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from django.test.utils import override_settings

from .backends import ModelBackend
from .compatibility import urlencode

try:
    import ua_parser
except ImportError:  # pragma: no cover
    ua_parser = None


SAFARI_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/12.1 Safari/605.1.15"
)


@override_settings(
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "sesame.middleware.AuthenticationMiddleware",
    ],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {
                "context_processors": ["django.contrib.auth.context_processors.auth"]
            },
        }
    ],
)
class TestMiddleware(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="john", password="doe")
        self.token = ModelBackend().create_token(self.user)
        self.bad_token = self.token.lower()

        self.log = io.StringIO()
        self.handler = logging.StreamHandler(self.log)
        self.logger = logging.getLogger("sesame")
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    redirect_enabled = True

    def assertUserLoggedIn(self, response, redirect_url=None):
        request = response.wsgi_request
        # User is logged in with django.contrib.sessions.
        self.assertEqual(get_user(request), self.user)
        # User is logged in with django.contrib.auth.
        self.assertEqual(request.user, self.user)

        if redirect_url is not None and self.redirect_enabled:
            self.assertRedirects(response, redirect_url)
        else:
            self.assertContains(response, self.user.username)

    def assertUserNotLoggedIn(self, response):
        request = response.wsgi_request
        self.assertIsInstance(get_user(request), AnonymousUser)
        self.assertIsInstance(request.user, AnonymousUser)

        self.assertContains(response, "anonymous")

    def test_token(self):
        response = self.client.get("/", {"url_auth_token": self.token})
        self.assertUserLoggedIn(response, redirect_url="/")

    def test_token_with_path_and_param(self):
        response = self.client.get("/foo", {"url_auth_token": self.token, "bar": 42})
        self.assertUserLoggedIn(response, redirect_url="/foo?bar=42")

    def test_token_in_POST_request(self):
        response = self.client.post("/?" + urlencode({"url_auth_token": self.token}))
        self.assertUserLoggedIn(response)

    @unittest.skipIf(ua_parser is None, "test requires ua-parser")
    def test_token_in_Safari_request(self):
        response = self.client.get(
            "/", {"url_auth_token": self.token}, HTTP_USER_AGENT=SAFARI_USER_AGENT
        )
        self.assertUserLoggedIn(response)

    def test_bad_token(self):
        response = self.client.get("/", {"url_auth_token": self.bad_token})
        self.assertUserNotLoggedIn(response)

    def test_no_token(self):
        response = self.client.get("/")
        self.assertUserNotLoggedIn(response)


@override_settings(
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "sesame.middleware.AuthenticationMiddleware",
    ]
)
class TestWithoutAuthMiddleware(TestMiddleware):

    # When django.contrib.auth isn't enabled, every URL must contain an
    # authentication token, so it mustn't be removed with a redirect.
    redirect_enabled = False


@override_settings(
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "sesame.middleware.AuthenticationMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ]
)
class TestBeforeAuthMiddleware(TestMiddleware):

    # When the sesame middleware is (incorrectly) before the
    # django.contrib.auth middleware, sesame doesn't know that
    # django.contrib.auth is enabled, so it's the same as when
    # django.contrib.auth isn't enabled.
    redirect_enabled = False


@override_settings(MIDDLEWARE=["sesame.middleware.AuthenticationMiddleware"])
class TestWithoutSessionMiddleware(TestMiddleware):
    def assertUserLoggedIn(self, response, redirect_url=None):
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertContains(response, self.user.username)

    def assertUserNotLoggedIn(self, response):
        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertContains(response, "anonymous")
