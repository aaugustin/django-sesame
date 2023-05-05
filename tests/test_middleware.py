import unittest

from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.test.utils import override_settings

from sesame.utils import get_parameters, get_query_string

from .mixins import CreateUserMixin
from .signals import reset_sesame_settings  # noqa

try:
    import ua_parser
except ImportError:  # pragma: no cover
    ua_parser = None


SAFARI_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/12.1 Safari/605.1.15"
)

CHROME_IOS_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) "
    "AppleWebKit/602.1.50 (KHTML, like Gecko) "
    "CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1"
)


@override_settings(
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "sesame.middleware.AuthenticationMiddleware",
    ],
)
class TestMiddleware(CreateUserMixin, TestCase):
    should_redirect_after_auth = True

    def assertUserLoggedIn(self, response, redirect_url):
        request = response.wsgi_request
        # User is logged in with django.contrib.sessions.
        self.assertEqual(get_user(request), self.user)
        # User is logged in with django.contrib.auth.
        self.assertEqual(request.user, self.user)

        if redirect_url is not None and self.should_redirect_after_auth:
            self.assertRedirects(response, redirect_url)
        else:
            self.assertContains(response, self.user.username)

    def assertUserNotLoggedIn(self, response):
        request = response.wsgi_request
        # User isn't logged in with django.contrib.sessions.
        self.assertIsInstance(get_user(request), AnonymousUser)
        # User isn't logged in with django.contrib.auth.
        self.assertIsInstance(request.user, AnonymousUser)

        self.assertContains(response, "anonymous")

    def test_token(self):
        response = self.client.get("/", get_parameters(self.user))
        self.assertUserLoggedIn(response, redirect_url="/")

    def test_no_token(self):
        response = self.client.get("/")
        self.assertUserNotLoggedIn(response)

    def test_empty_token(self):
        response = self.client.get("/", {"sesame": ""})
        self.assertUserNotLoggedIn(response)

    def test_bad_token(self):
        params = get_parameters(self.user)
        params["sesame"] = params["sesame"].lower()
        response = self.client.get("/", params)
        self.assertUserNotLoggedIn(response)

    @override_settings(SESAME_ONE_TIME=True)
    def test_one_time_token(self):
        response = self.client.get("/", get_parameters(self.user))
        self.assertUserLoggedIn(response, redirect_url="/")

    def test_reuse_token(self):
        params = get_parameters(self.user)
        response = self.client.get("/", params)
        self.assertUserLoggedIn(response, redirect_url="/")
        self.client.logout()
        response = self.client.get("/", params)
        self.assertUserLoggedIn(response, redirect_url="/")

    @override_settings(SESAME_ONE_TIME=True)
    def test_reuse_one_time_token(self):
        params = get_parameters(self.user)
        response = self.client.get("/", params)
        self.assertUserLoggedIn(response, redirect_url="/")
        self.client.logout()
        response = self.client.get("/", params)
        self.assertUserNotLoggedIn(response)

    # one query to get the user matching the token
    # one query to update their last login date
    NUM_QUERIES = 2

    def test_token_num_queries(self):
        with self.assertNumQueries(self.NUM_QUERIES):
            response = self.client.get("/", get_parameters(self.user))
        self.assertUserLoggedIn(response, redirect_url="/")

    ONE_TIME_NUM_QUERIES = 2

    @override_settings(SESAME_ONE_TIME=True)
    def test_one_time_token_num_queries(self):
        with self.assertNumQueries(self.ONE_TIME_NUM_QUERIES):
            response = self.client.get("/", get_parameters(self.user))
        self.assertUserLoggedIn(response, redirect_url="/")

    def test_token_with_path_and_params(self):
        params = get_parameters(self.user)
        params["bar"] = 42
        response = self.client.get("/foo", params)
        self.assertUserLoggedIn(response, redirect_url="/foo?bar=42")

    def test_token_in_POST_request(self):
        response = self.client.post("/" + get_query_string(self.user))
        self.assertUserLoggedIn(response, redirect_url=None)

    @unittest.skipIf(ua_parser is None, "test requires ua-parser")
    def test_token_in_Safari_request(self):
        response = self.client.get(
            "/", get_parameters(self.user), HTTP_USER_AGENT=SAFARI_USER_AGENT
        )
        self.assertUserLoggedIn(response, redirect_url=None)

    @unittest.skipIf(ua_parser is None, "test requires ua-parser")
    def test_token_in_iOS_request(self):
        response = self.client.get(
            "/", get_parameters(self.user), HTTP_USER_AGENT=CHROME_IOS_USER_AGENT
        )
        self.assertUserLoggedIn(response, redirect_url=None)


@override_settings(
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "sesame.middleware.AuthenticationMiddleware",
    ]
)
class TestWithoutAuthMiddleware(TestMiddleware):
    # When django.contrib.auth isn't enabled, every URL must contain an
    # authentication token, so it mustn't be removed with a redirect.
    should_redirect_after_auth = False


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
    should_redirect_after_auth = False

    # Furthermore, the django.contrib.auth middleware overrides the
    # ``request.user`` attribute set by the sesame middleware via
    # ``login(request, user)``, which causes a duplicate query.
    NUM_QUERIES = TestMiddleware.NUM_QUERIES + 1
    ONE_TIME_NUM_QUERIES = TestMiddleware.ONE_TIME_NUM_QUERIES + 1


@override_settings(MIDDLEWARE=["sesame.middleware.AuthenticationMiddleware"])
class TestWithoutSessionMiddleware(TestMiddleware):
    def assertUserLoggedIn(self, response, redirect_url=None):
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertContains(response, self.user.username)

    def assertUserNotLoggedIn(self, response):
        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertContains(response, "anonymous")

    # The last login date isn't updated when the session middleware isn't
    # enabled, except for one-time tokens.
    NUM_QUERIES = TestMiddleware.NUM_QUERIES - 1
