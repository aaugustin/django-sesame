import base64
import datetime
import unittest.mock

from django.test import TestCase, override_settings
from django.utils import timezone

from sesame import packers
from sesame.tokens_v2 import (
    TIMESTAMP_OFFSET,
    create_token,
    detect_token,
    get_revocation_key,
    parse_token,
)

from .mixins import CaptureLogMixin, CreateUserMixin
from .signals import reset_sesame_settings  # noqa


class TestTokensV2(CaptureLogMixin, CreateUserMixin, TestCase):
    def test_valid_token(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john in default scope")

    # Test invalid tokens

    @override_settings(SESAME_MAX_AGE=300)
    def test_invalid_base64_string(self):
        token = "deadbeef-"
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token: cannot decode token")

    @override_settings(SESAME_MAX_AGE=300)
    def test_truncated_token_in_primary_key(self):
        token = create_token(self.user)
        # Primary key is in bytes 0 - 5 1/3
        token = token[:4]
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token: cannot extract primary key")

    @override_settings(SESAME_MAX_AGE=300)
    def test_truncated_token_in_timestamp(self):
        token = create_token(self.user)
        # Timestamp is in bytes 5 1/3 - 10 2/3
        token = token[:8]
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token: cannot extract timestamp")

    @override_settings(SESAME_MAX_AGE=300)
    def test_truncated_token_in_signature(self):
        token = create_token(self.user)
        # Signature is in bytes 10 2/3 - 24
        token = token[:12]
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token: cannot extract signature")

    def test_invalid_signature(self):
        token = create_token(self.user)
        # Alter signature, which is in bytes 5 1/3 - 18 2/3
        token = token[:6] + token[6:].lower()
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user john in default scope")

    @override_settings(SESAME_MAX_AGE=300)
    def test_random_token(self):
        token = "!@#$" * 6
        self.assertEqual(len(token), len(create_token(self.user)))
        self.assertFalse(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token")

    def test_unknown_user(self):
        token = create_token(self.user)
        self.user.delete()
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Unknown or inactive user: pk = 1")

    # Test token expiry

    @override_settings(SESAME_MAX_AGE=300)
    def test_valid_max_age_token(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john in default scope")

    @override_settings(SESAME_MAX_AGE=-300)
    def test_expired_max_age_token(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Expired token")

    @override_settings(SESAME_MAX_AGE=-300)
    def test_extended_max_age_token(self):
        token = create_token(self.user)
        with override_settings(SESAME_MAX_AGE=300):
            self.assertTrue(detect_token(token))
            user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john in default scope")

    @override_settings(SESAME_MAX_AGE=300)
    def test_max_age_token_without_timestamp(self):
        with override_settings(SESAME_MAX_AGE=None):
            token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token: cannot extract signature")

    def test_token_with_timestamp(self):
        with override_settings(SESAME_MAX_AGE=300):
            token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token: cannot extract signature")

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
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user john in default scope")

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
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user john in default scope")

    @override_settings(SESAME_INVALIDATE_ON_PASSWORD_CHANGE=False)
    def test_valid_token_after_password_change(self):
        token = create_token(self.user)
        self.user.set_password("hunter2")
        self.user.save()
        user = parse_token(token, self.get_user)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john in default scope")

    # Test scoped tokens

    def test_valid_scoped_token_in_scope(self):
        token = create_token(self.user, scope="test")
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user, scope="test")
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john in scope test")

    def test_invalid_scoped_token_in_other_scope(self):
        token = create_token(self.user, scope="test")
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user, scope="other")
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user john in scope other")

    def test_invalid_scoped_token_in_default_scope(self):
        token = create_token(self.user, scope="test")
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user john in default scope")

    def test_invalid_token_in_scope(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user, scope="test")
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user john in scope test")

    # Test custom max_age

    @override_settings(SESAME_MAX_AGE=-300)
    def test_custom_max_age(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user, max_age=300)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john")

    @override_settings(SESAME_MAX_AGE=-300)
    def test_custom_max_age_timedelta(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        max_age = datetime.timedelta(seconds=300)
        user = parse_token(token, self.get_user, max_age=max_age)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Valid token for user john")

    def test_custom_max_age_ignored(self):
        token = create_token(self.user)
        self.assertTrue(detect_token(token))
        user = parse_token(token, self.get_user, max_age=-300)
        self.assertEqual(user, self.user)
        self.assertLogsContain("Ignoring max_age argument")
        self.assertLogsContain("Valid token for user john")

    # Test custom primary key packer

    @override_settings(
        AUTH_USER_MODEL="tests.StrUser",
        SESAME_PACKER="tests.test_packers.Packer",
    )
    def test_custom_packer_is_used(self):
        # CreateUserMixin.setUp() ran before @override_settings changed the
        # user model.
        user = self.create_user(username="abcdef012345abcdef567890")
        token = create_token(user)
        # base64.b64encode(bytes.fromhex(username)).decode() == "q83vASNFq83vVniQ"
        self.assertEqual(token[:16], "q83vASNFq83vVniQ")
        self.assertTrue(detect_token(token))

    def test_custom_packer_change(self):
        token = create_token(self.user)
        with override_settings(SESAME_PACKER="tests.test_packers.RepeatPacker"):
            user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Bad token: cannot extract primary key")

    # Miscellaneous tests

    @staticmethod
    def decode_token(token):
        token = token.encode()
        return base64.urlsafe_b64decode(token + b"=" * (-len(token) % 4))

    @staticmethod
    def encode_token(data):
        token = base64.urlsafe_b64encode(data).rstrip(b"=")
        return token.decode()

    def test_key_change_invalidates_tokens(self):
        """Token signature changes if SESAME_KEY changes."""
        token = create_token(self.user)
        with override_settings(SESAME_KEY="new"):
            user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user john in default scope")

    def test_primary_key_and_timestamp_confusion(self):
        """Token signature changes if SESAME_MAX_AGE is enabled or disabled."""
        TIME = TIMESTAMP_OFFSET + (1 << 24)
        user1 = self.user
        with override_settings(SESAME_MAX_AGE=300):
            with unittest.mock.patch("time.time", return_value=TIME):
                token1 = create_token(user1)

        with override_settings(AUTH_USER_MODEL="tests.BigAutoUser"):
            user2 = self.create_user("jane", pk=(user1.pk << 32) + (1 << 24))
            token2 = create_token(user2)
            # Duplicate user1 in the BigAutoUser table.
            user1.__class__ = user2.__class__
            user1.save()

        # The first 8 bytes are the same:
        # - token1: primary key of user1 and timestamp
        # - token2: primary key of user2
        self.assertEqual(self.decode_token(token1)[:8], self.decode_token(token2)[:8])

        with override_settings(AUTH_USER_MODEL="tests.BigAutoUser"):
            user = parse_token(token1, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user jane")

        with override_settings(SESAME_MAX_AGE=300):
            with unittest.mock.patch("time.time", return_value=TIME + 1):
                user = parse_token(token2, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user john in default scope")

    def test_packer_confusion(self):
        """Token signature changes if SESAME_PACKER changes."""
        user1 = self.user
        with override_settings(SESAME_PACKER="tests.test_packers.RepeatPacker"):
            token1 = create_token(user1)
        user2 = self.create_user("jane", pk=(user1.pk << 16) + user1.pk)
        token2 = create_token(user2)

        # The first 4 bytes are the same:
        # - token1: primary key of user1 encoded with RepeatPacker
        # - token2: primary key of user2
        self.assertEqual(self.decode_token(token1)[:4], self.decode_token(token2)[:4])

        user = parse_token(token1, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user jane")

        with override_settings(SESAME_PACKER="tests.test_packers.RepeatPacker"):
            user = parse_token(token2, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user john in default scope")

    @override_settings(SESAME_INVALIDATE_ON_PASSWORD_CHANGE=False)
    def test_naive_token_hijacking_fails(self):
        # The revocation key may be identical for two users:
        # - if SESAME_INVALIDATE_ON_PASSWORD_CHANGE is False or if they don't
        #   have a password;
        # - if SESAME_ONE_TIME is False, which is the default, or if they have
        #   the same last_login.
        # In that case, could one user could impersonate the other?
        user1 = self.user
        user2 = self.create_user("jane")

        token1 = create_token(user1)
        token2 = create_token(user2)

        # Check that the test scenario produces identical revocation keys.
        self.assertEqual(get_revocation_key(user1), get_revocation_key(user2))

        # Check that changing just the PK doesn't allow hijacking the other
        # user's account -- because the PK is included in the signature.
        data1 = self.decode_token(token1)
        data2 = self.decode_token(token2)
        self.assertEqual(data1[:4], packers.packer.pack_pk(user1.pk))
        self.assertEqual(data2[:4], packers.packer.pack_pk(user2.pk))

        # Check that changing just the primary key doesn't allow hijacking the
        # other user's account.
        token = self.encode_token(data2[:4] + data1[4:])

        user = parse_token(token, self.get_user)
        self.assertIsNone(user)
        self.assertLogsContain("Invalid token for user jane")
