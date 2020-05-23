from django.test import RequestFactory, TestCase, override_settings

from .test_mixins import CaptureLogMixin, CreateUserMixin
from .test_signals import reset_sesame_settings  # noqa
from .utils import get_parameters, get_query_string, get_user


class TestUtils(CaptureLogMixin, CreateUserMixin, TestCase):
    def test_get_parameters(self):
        self.assertEqual(list(get_parameters(self.user)), ["sesame"])

    def test_get_query_string(self):
        self.assertIn("?sesame=", get_query_string(self.user))

    def get_request_with_token(self):
        return RequestFactory().get("/" + get_query_string(self.user))

    def test_get_user(self):
        request = self.get_request_with_token()
        self.assertEqual(get_user(request), self.user)

    def test_get_user_no_token(self):
        request = RequestFactory().get("/")
        self.assertIsNone(get_user(request))

    def test_get_user_empty_token(self):
        request = RequestFactory().get("/sesame=")
        self.assertIsNone(get_user(request))

    def test_get_user_bad_token(self):
        request = RequestFactory().get("/" + get_query_string(self.user).lower())
        self.assertIsNone(get_user(request))
        self.assertIn("Bad token", self.get_log())

    def test_get_user_bad_token(self):
        request = RequestFactory().get("/" + get_query_string(self.user).lower())
        self.assertIsNone(get_user(request))
        self.assertIn("Bad token", self.get_log())

    @override_settings(SESAME_MAX_AGE=-10)
    def test_get_user_expired_token(self):
        request = self.get_request_with_token()
        self.assertIsNone(get_user(request))
        self.assertIn("Expired token", self.get_log())

    def test_get_user_inactive_user(self):
        request = self.get_request_with_token()
        self.user.is_active = False
        self.user.save()
        self.assertIsNone(get_user(request))
        self.assertIn("Unknown or inactive user", self.get_log())

    def test_get_user_unknown_user(self):
        request = self.get_request_with_token()
        self.user.delete()
        self.assertIsNone(get_user(request))
        self.assertIn("Unknown or inactive user", self.get_log())

    def test_get_user_does_not_invalidate_tokens(self):
        request = self.get_request_with_token()
        self.assertEqual(get_user(request), self.user)
        self.assertEqual(get_user(request), self.user)

    @override_settings(SESAME_ONE_TIME=True)
    def test_get_user_invalidates_one_time_tokens(self):
        request = self.get_request_with_token()
        self.assertEqual(get_user(request), self.user)
        self.assertIsNone(get_user(request))
        self.assertIn("Invalid token", self.get_log())

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
