from django.test import TestCase, override_settings

from sesame import tokens_v1, tokens_v2
from sesame.tokens import create_token, parse_token

from .mixins import CaptureLogMixin, CreateUserMixin
from .signals import reset_sesame_settings  # noqa


class TestUtils(CaptureLogMixin, CreateUserMixin, TestCase):
    def test_create_token_default_v2(self):
        token = create_token(self.user)
        self.assertTrue(tokens_v2.detect_token(token))
        self.assertFalse(tokens_v1.detect_token(token))

    @override_settings(SESAME_TOKENS=["sesame.tokens_v2"])
    def test_create_token_force_v2(self):
        token = create_token(self.user)
        self.assertTrue(tokens_v2.detect_token(token))
        self.assertFalse(tokens_v1.detect_token(token))

    @override_settings(SESAME_TOKENS=["sesame.tokens_v1"])
    def test_create_token_force_v1(self):
        token = create_token(self.user)
        self.assertTrue(tokens_v1.detect_token(token))
        self.assertFalse(tokens_v2.detect_token(token))

    @override_settings(SESAME_TOKENS=["sesame.tokens_v1", "sesame.tokens_v2"])
    def test_create_token_use_first_choice(self):
        token = create_token(self.user)
        self.assertTrue(tokens_v1.detect_token(token))
        self.assertFalse(tokens_v2.detect_token(token))

    def test_parse_token_accepts_v2(self):
        token = create_token(self.user)
        user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john")

    def test_parse_token_accepts_v1(self):
        with override_settings(SESAME_TOKENS=["sesame.tokens_v1"]):
            token = create_token(self.user)
        user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john")

    @override_settings(SESAME_TOKENS=["sesame.tokens_v2"])
    def test_parse_token_force_v2(self):
        with override_settings(SESAME_TOKENS=["sesame.tokens_v1"]):
            token = create_token(self.user)
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token: doesn't match a supported format")

    @override_settings(SESAME_TOKENS=["sesame.tokens_v1"])
    def test_parse_token_force_v1(self):
        with override_settings(SESAME_TOKENS=["sesame.tokens_v2"]):
            token = create_token(self.user)
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token: doesn't match a supported format")
