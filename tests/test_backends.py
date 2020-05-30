from django.test import TestCase

from sesame.backends import ModelBackend
from sesame.tokens_v1 import create_token

from .mixins import CaptureLogMixin, CreateUserMixin


class TestModelBackend(CaptureLogMixin, CreateUserMixin, TestCase):
    def test_token(self):
        token = create_token(self.user)
        user = ModelBackend().authenticate(request=None, sesame=token)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john")

    def test_no_token(self):
        user = ModelBackend().authenticate(request=None, sesame=None)
        self.assertIsNone(user)
        self.assertNoLogs()

    def test_emtpy_token(self):
        user = ModelBackend().authenticate(request=None, sesame="")
        self.assertIsNone(user)
        self.assertLogsContain("Bad token")

    def test_bad_token(self):
        token = create_token(self.user)
        user = ModelBackend().authenticate(request=None, sesame=token.lower())
        self.assertIsNone(user)
        self.assertLogsContain("Bad token")

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        token = create_token(self.user)
        user = ModelBackend().authenticate(request=None, sesame=token)
        self.assertIsNone(user)
        self.assertLogsContain("Unknown or inactive user")
