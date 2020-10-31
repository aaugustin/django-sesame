import datetime

from django.core import signing
from django.test import TestCase, override_settings
from django.utils import timezone

from sesame import packers
from sesame.tokens_v1 import create_token, detect_token, parse_token

from .mixins import CaptureLogMixin, CreateUserMixin
from .signals import reset_sesame_settings  # noqa


class TestTokensV1(CaptureLogMixin, CreateUserMixin, TestCase):
    def test_valid_token(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john")

    # Test invalid tokens

    def test_invalid_signature(self):
        token = create_token(self.user)
        # Alter signature, which is is in bytes 28 - 55
        token = token[:28] + token[28:].lower()
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Bad token")

    def test_random_token(self):
        token = "!@#$%" * 11
        self.assertEqual(len(token), len(create_token(self.user)))
        self.assertFalse(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Bad token")

    def test_unknown_user(self):
        token = create_token(self.user)
        self.user.delete()
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Unknown or inactive user")

    # Test token expiry

    @override_settings(SESAME_MAX_AGE=300)
    def test_valid_max_age_token(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john")

    @override_settings(SESAME_MAX_AGE=-300)
    def test_expired_max_age_token(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Expired token")

    @override_settings(SESAME_MAX_AGE=-300)
    def test_extended_max_age_token(self):
        token = create_token(self.user)
        with override_settings(SESAME_MAX_AGE=300):
            self.assertTrue(detect_token(token))
            user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john")

    @override_settings(SESAME_MAX_AGE=300)
    def test_max_age_token_without_timestamp(self):
        with override_settings(SESAME_MAX_AGE=None):
            token = create_token(self.user)
        self.assertFalse(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Valid signature but unexpected token")

    def test_token_with_timestamp(self):
        with override_settings(SESAME_MAX_AGE=300):
            token = create_token(self.user)
        self.assertFalse(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Valid signature but unexpected token")

    # Test one-time tokens

    @override_settings(SESAME_ONE_TIME=True)
    def test_valid_one_time_token(self):
        self.test_valid_token()

    @override_settings(SESAME_ONE_TIME=True)
    def test_valid_one_time_token_when_user_never_logged_in(self):
        self.user.last_login = None
        self.user.save()
        self.test_valid_token()

    @override_settings(SESAME_ONE_TIME=True)
    def test_one_time_token_invalidation_when_last_login_date_changes(self):
        token = create_token(self.user)
        self.user.last_login = timezone.now() - datetime.timedelta(1800)
        self.user.save()
        user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Invalid token")

    # Test token invalidation on password change

    def test_valid_token_when_user_has_no_password(self):
        self.user.password = ""
        self.user.save()
        self.test_valid_token()

    def test_valid_token_when_user_has_unusable_password(self):
        self.user.set_unusable_password()
        self.user.save()
        self.test_valid_token()

    def test_invalid_token_after_password_change(self):
        token = create_token(self.user)
        self.user.set_password("hunter2")
        self.user.save()
        user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Invalid token")

    @override_settings(SESAME_INVALIDATE_ON_PASSWORD_CHANGE=False)
    def test_valid_token_after_password_change(self):
        token = create_token(self.user)
        self.user.set_password("hunter2")
        self.user.save()
        user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john")

    # Test custom primary key packer

    @override_settings(
        AUTH_USER_MODEL="tests.StrUser",
        SESAME_PACKER="tests.test_packers.Packer",
    )
    def test_custom_packer_is_used(self):
        user = self.create_user(username="abcdef012345abcdef567890")
        token = create_token(user)
        # base64.b64encode(bytes.fromhex(username)).decode() == "q83vASNFq83vVniQ"
        self.assertEqual(token[:16], "q83vASNFq83vVniQ")
        self.assertTrue(detect_token(token))

    def test_custom_packer_change(self):
        token = create_token(self.user)
        with override_settings(SESAME_PACKER="tests.test_packers.RepeatPacker"):
            user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Valid signature but unexpected token")

    # Miscellaneous tests

    @override_settings(SESAME_INVALIDATE_ON_PASSWORD_CHANGE=False)
    def test_naive_token_hijacking_fails(self):
        # The revocation key may be identical for two users:
        # - if SESAME_INVALIDATE_ON_PASSWORD_CHANGE is False or if they don't
        #   have a password;
        # - if SESAME_ONE_TIME is False or if they have the same last_login.
        # In that case, could one user could impersonate the other?
        user1 = self.user
        user2 = self.create_user("jane")

        token1 = create_token(user1)
        token2 = create_token(user2)

        # Check that the test scenario produces identical revocation keys.
        # This test depends on the implementation of django.core.signing;
        # however, the format of tokens must be stable to keep them valid.
        data1, sig1 = token1.split(":", 1)
        data2, sig2 = token2.split(":", 1)
        data1 = signing.b64_decode(data1.encode())
        data2 = signing.b64_decode(data2.encode())
        pk1 = packers.packer.pack_pk(user1.pk)
        pk2 = packers.packer.pack_pk(user2.pk)
        self.assertEqual(data1[: len(pk1)], pk1)
        self.assertEqual(data2[: len(pk2)], pk2)
        key1 = data1[len(pk1) :]
        key2 = data2[len(pk2) :]
        self.assertEqual(key1, key2)

        # Check that changing just the primary key doesn't allow hijacking the
        # other user's account.
        data = pk2 + key1
        data = signing.b64_encode(data).decode()
        token = data + sig1
        user = parse_token(token, self.get_user)
        self.assertEqual(user, None)
        self.assertLogsContain("Bad token")
