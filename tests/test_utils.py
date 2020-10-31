from django.test import RequestFactory, TestCase, override_settings

from sesame.utils import get_parameters, get_query_string, get_token, get_user

from .mixins import CaptureLogMixin, CreateUserMixin
from .signals import reset_sesame_settings  # noqa


class TestUtils(CaptureLogMixin, CreateUserMixin, TestCase):
    def test_get_token(self):
        self.assertIsInstance(get_token(self.user), str)

    def test_get_scoped_token(self):
        self.assertIsInstance(get_token(self.user, scope="test"), str)

    def test_get_parameters(self):
        self.assertEqual(get_parameters(self.user), {"sesame": get_token(self.user)})

    def test_get_parameters_with_scope(self):
        self.assertEqual(
            get_parameters(self.user, scope="test"),
            {"sesame": get_token(self.user, scope="test")},
        )

    def test_get_query_string(self):
        # Tokens v2 only contain URL-safe characters. There's no escaping.
        self.assertEqual(get_query_string(self.user), "?sesame=" + get_token(self.user))

    def test_get_query_string_with_scope(self):
        # Tokens v2 only contain URL-safe characters. There's no escaping.
        self.assertEqual(
            get_query_string(self.user, scope="test"),
            "?sesame=" + get_token(self.user, scope="test"),
        )

    def get_request_with_token(self):
        return RequestFactory().get("/", get_parameters(self.user))

    def test_get_user(self):
        request = self.get_request_with_token()
        self.assertEqual(get_user(request), self.user)

    def test_get_user_no_token(self):
        request = RequestFactory().get("/")
        self.assertIsNone(get_user(request))

    def test_get_user_empty_token(self):
        request = RequestFactory().get("/", {"sesame": ""})
        self.assertIsNone(get_user(request))

    def test_get_user_bad_token(self):
        request = RequestFactory().get("/", {"sesame": "~!@#$%^&*~!@#$%^&*~"})
        self.assertIsNone(get_user(request))
        self.assertLogsContain("Bad token")

    @override_settings(SESAME_MAX_AGE=-10)
    def test_get_user_expired_token(self):
        request = self.get_request_with_token()
        self.assertIsNone(get_user(request))
        self.assertLogsContain("Expired token")

    def test_get_user_inactive_user(self):
        request = self.get_request_with_token()
        self.user.is_active = False
        self.user.save()
        self.assertIsNone(get_user(request))
        self.assertLogsContain("Unknown or inactive user")

    def test_get_user_unknown_user(self):
        request = self.get_request_with_token()
        self.user.delete()
        self.assertIsNone(get_user(request))
        self.assertLogsContain("Unknown or inactive user")

    def test_get_user_does_not_invalidate_tokens(self):
        request = self.get_request_with_token()
        self.assertEqual(get_user(request), self.user)
        self.assertEqual(get_user(request), self.user)

    @override_settings(SESAME_ONE_TIME=True)
    def test_get_user_invalidates_one_time_tokens(self):
        request = self.get_request_with_token()
        self.assertEqual(get_user(request), self.user)
        self.assertIsNone(get_user(request))
        self.assertLogsContain("Invalid token")

    def test_get_user_does_not_update_last_login(self):
        request = self.get_request_with_token()
        last_login = self.user.last_login
        self.assertEqual(get_user(request), self.user)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_login, last_login)

    @override_settings(SESAME_ONE_TIME=True)
    def test_get_user_updates_last_login_for_one_time_tokens(self):
        request = self.get_request_with_token()
        last_login = self.user.last_login
        self.assertEqual(get_user(request), self.user)
        self.user.refresh_from_db()
        self.assertGreater(self.user.last_login, last_login)

    def test_get_user_force_update_last_login(self):
        request = self.get_request_with_token()
        last_login = self.user.last_login
        self.assertEqual(get_user(request, update_last_login=True), self.user)
        self.user.refresh_from_db()
        self.assertGreater(self.user.last_login, last_login)

    @override_settings(SESAME_ONE_TIME=True)
    def test_get_user_force_not_update_last_login(self):
        request = self.get_request_with_token()
        last_login = self.user.last_login
        self.assertEqual(get_user(request, update_last_login=False), self.user)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_login, last_login)
