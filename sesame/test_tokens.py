import datetime
import io
import logging

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import TestCase, override_settings
from django.utils import timezone

from .packers import BasePacker
from .tokens import create_token, parse_token, packer


class CaptureLogMixin:
    def setUp(self):
        super().setUp()
        self.log = io.StringIO()
        self.handler = logging.StreamHandler(self.log)
        self.logger = logging.getLogger("sesame")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def get_log(self):
        self.handler.flush()
        return self.log.getvalue()

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        super().tearDown()


def get_user(user_id):
    User = get_user_model()
    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        return None


class TestTokens(CaptureLogMixin, TestCase):

    username = "john"

    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.user = User.objects.create(
            username=self.username,
            last_login=timezone.now() - datetime.timedelta(3600),
        )

    def test_valid_token(self):
        token = create_token(self.user)
        user = parse_token(token, get_user)
        self.assertEqual(user, self.user)
        self.assertIn("Valid token for user %s" % self.username, self.get_log())

    def test_bad_token(self):
        token = create_token(self.user)
        user = parse_token(token.lower(), get_user)
        self.assertEqual(user, None)
        self.assertIn("Bad token", self.get_log())

    def test_unknown_user(self):
        token = create_token(self.user)
        self.user.delete()
        user = parse_token(token, get_user)
        self.assertEqual(user, None)
        self.assertIn("Unknown or inactive user", self.get_log())

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        token = create_token(self.user)
        user = parse_token(token, get_user)
        self.assertEqual(user, None)
        self.assertIn("Unknown or inactive user", self.get_log())

    def test_password_change(self):
        token = create_token(self.user)
        self.user.set_password("hunter2")
        self.user.save()
        user = parse_token(token, get_user)
        self.assertEqual(user, None)
        self.assertIn("Invalid token", self.get_log())


@override_settings(SESAME_MAX_AGE=10)
class TestTokensWithExpiry(TestTokens):
    @override_settings(SESAME_MAX_AGE=-10)
    def test_expired_token(self):
        token = create_token(self.user)
        user = parse_token(token, get_user)
        self.assertEqual(user, None)
        self.assertIn("Expired token", self.get_log())

    def test_token_without_timestamp(self):
        with override_settings(SESAME_MAX_AGE=None):
            token = create_token(self.user)
        user = parse_token(token, get_user)
        self.assertEqual(user, None)
        self.assertIn("Valid signature but unexpected token", self.get_log())


@override_settings(SESAME_ONE_TIME=True)
class TestTokensWithOneTime(TestTokens):
    def test_no_last_login(self):
        self.user.last_login = None
        self.user.save()
        token = create_token(self.user)
        user = parse_token(token, get_user)
        self.assertEqual(user, self.user)
        self.assertIn("Valid token for user %s" % self.username, self.get_log())

    def test_last_login_change(self):
        token = create_token(self.user)
        self.user.last_login = timezone.now() - datetime.timedelta(1800)
        self.user.save()
        user = parse_token(token, get_user)
        self.assertEqual(user, None)
        self.assertIn("Invalid token", self.get_log())


@override_settings(SESAME_INVALIDATE_ON_PASSWORD_CHANGE=False, SESAME_MAX_AGE=3600)
class TestTokensWithoutInvalidateOnPasswordChange(TestTokens):
    def test_password_change(self):
        token = create_token(self.user)
        self.user.set_password("hunter2")
        self.user.save()
        user = parse_token(token, get_user)
        self.assertEqual(user, self.user)
        self.assertIn("Valid token for user %s" % self.username, self.get_log())


@override_settings(AUTH_USER_MODEL="test_app.BigAutoUser")
class TestTokensWithBigAutoPrimaryKey(TestTokens):

    pass


@override_settings(AUTH_USER_MODEL="test_app.UUIDUser")
class TestTokensWithUUIDPrimaryKey(TestTokens):

    pass


class Packer(BasePacker):
    """
    Verbatim copy of the example in the README.

    """

    @staticmethod
    def pack_pk(user_pk):
        assert len(user_pk) == 24
        return bytes.fromhex(user_pk)

    @staticmethod
    def unpack_pk(data):
        return data[:12].hex(), data[12:]


@override_settings(
    AUTH_USER_MODEL="test_app.StrUser", SESAME_PACKER=__name__ + ".Packer",
)
class TestTokensWithCustomPacker(TestTokens):

    username = "abcdef012345abcdef567890"

    def test_custom_packer_is_used(self):
        token = create_token(self.user)
        # base64.b64encode(bytes.fromhex(username)).decode() == "q83vASNFq83vVniQ"
        self.assertEqual(token[:16], "q83vASNFq83vVniQ")



class TestTokensWithUnsupportedPrimaryKey(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username=True)

    def test_authenticate(self):
        with self.assertRaises(NotImplementedError) as exc:
            # The exception is raised in override_settings,
            # when django-sesame initializes the tokenizer
            with override_settings(AUTH_USER_MODEL="test_app.BooleanUser"):
                create_token(self.user)

        self.assertEqual(
            str(exc.exception), "BooleanField primary keys aren't supported",
        )


class TestMisc(CaptureLogMixin, TestCase):
    def test_naive_token_hijacking_fails(self):
        # Tokens contain the PK of the user, the hash of the revocation key,
        # and a signature. The revocation key may be identical for two users:
        # - if SESAME_INVALIDATE_ON_PASSWORD_CHANGE is False or if they don't
        #   have a password;
        # - if SESAME_ONE_TIME is False or if they have the same last_login.
        User = get_user_model()
        last_login = timezone.now() - datetime.timedelta(3600)
        user_1 = User.objects.create(username="john", last_login=last_login)
        user_2 = User.objects.create(username="jane", last_login=last_login)

        token1 = create_token(user_1)
        token2 = create_token(user_2)

        # Check that the test scenario produces identical revocation keys.
        # This test depends on the implementation of django.core.signing;
        # however, the format of tokens must be stable to keep them valid.
        data1, sig1 = token1.split(":", 1)
        data2, sig2 = token2.split(":", 1)
        bin_data1 = signing.b64_decode(data1.encode())
        bin_data2 = signing.b64_decode(data2.encode())
        pk1 = packer.pack_pk(user_1.pk)
        pk2 = packer.pack_pk(user_2.pk)
        self.assertEqual(bin_data1[: len(pk1)], pk1)
        self.assertEqual(bin_data2[: len(pk2)], pk2)
        key1 = bin_data1[len(pk1) :]
        key2 = bin_data2[len(pk2) :]
        self.assertEqual(key1, key2)

        # Check that changing just the PK doesn't allow hijacking the other
        # user's account -- because the PK is included in the signature.
        bin_data = pk2 + key1
        data = signing.b64_encode(bin_data).decode()
        token = data + sig1
        user = parse_token(token, get_user)
        self.assertEqual(user, None)
        self.assertIn("Bad token", self.get_log())
