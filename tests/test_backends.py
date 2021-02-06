from django.test import TestCase, override_settings

from sesame.backends import ModelBackend
from sesame.tokens import create_token

from .mixins import CaptureLogMixin, CreateUserMixin


class TestModelBackend(CaptureLogMixin, CreateUserMixin, TestCase):
    def test_token(self):
        token = create_token(self.user)
        user = ModelBackend().authenticate(request=None, sesame=token)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john in default scope")

    @override_settings(SESAME_MAX_AGE=300)
    def test_token_with_max_age(self):
        token = create_token(self.user)
        user = ModelBackend().authenticate(request=None, sesame=token)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john in default scope")

    def test_no_token(self):
        token = None
        user = ModelBackend().authenticate(request=None, sesame=token)
        self.assertIsNone(user)
        self.assertNoLogs()

    def test_emtpy_token(self):
        token = ""
        user = ModelBackend().authenticate(request=None, sesame=token)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token")

    def test_bad_token(self):
        token = "~!@#$%^&*~!@#$%^&*~"
        user = ModelBackend().authenticate(request=None, sesame=token)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token")

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        token = create_token(self.user)
        user = ModelBackend().authenticate(request=None, sesame=token)
        self.assertIsNone(user)
        self.assertLogsContain("Unknown or inactive user")

    def test_scoped_token(self):
        token = create_token(self.user, scope="test")
        user = ModelBackend().authenticate(request=None, sesame=token, scope="test")
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john in scope test")

    @override_settings(SESAME_MAX_AGE=300)
    def test_token_with_max_age_override(self):
        token = create_token(self.user)
        user = ModelBackend().authenticate(request=None, sesame=token, max_age=-300)
        self.assertIsNone(user)
        self.assertLogsContain("Expired token")
