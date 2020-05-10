import datetime
import io
import logging

from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.utils import timezone

from .backends import ModelBackend


class TestModelBackend(TestCase):
    def setUp(self):
        self.backend = ModelBackend()

        User = get_user_model()
        self.user = User.objects.create(
            username="john", last_login=timezone.now() - datetime.timedelta(3600)
        )

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

    def test_authenticate(self):
        token = self.backend.create_token(self.user)
        user = self.backend.authenticate(request=None, url_auth_token=token)
        self.assertEqual(user, self.user)

    def test_valid_token(self):
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, self.user)
        self.assertIn("Valid token for user john", self.get_log())

    def test_bad_token(self):
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token.lower())
        self.assertEqual(user, None)
        self.assertIn("Bad token", self.get_log())

    def test_unknown_user(self):
        token = self.backend.create_token(self.user)
        self.user.delete()
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Unknown or inactive user", self.get_log())

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Unknown or inactive user", self.get_log())

    def test_password_change(self):
        token = self.backend.create_token(self.user)
        self.user.set_password("hunter2")
        self.user.save()
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Invalid token", self.get_log())

    def test_naive_token_hijacking_fails(self):
        # Tokens contain the PK of the user, the hash of the revocation key,
        # and a signature. The revocation key may be identical for two users:
        # - if SESAME_INVALIDATE_ON_PASSWORD_CHANGE is False or if they don't
        #   have a password;
        # - if SESAME_ONE_TIME is False or if they have the same last_login.
        similar_user = type(self.user).objects.create(
            username="jane", last_login=self.user.last_login
        )

        token1 = self.backend.create_token(self.user)
        token2 = self.backend.create_token(similar_user)
        self.backend.unsign(token1)
        self.backend.unsign(token2)

        # Check that the test scenario produces identical revocation keys.
        # This test depends on the implementation of django.core.signing;
        # however, the format of tokens must be stable to keep them valid.
        data1, sig1 = token1.split(self.backend.signer.sep, 1)
        data2, sig2 = token2.split(self.backend.signer.sep, 1)
        bin_data1 = signing.b64_decode(data1.encode())
        bin_data2 = signing.b64_decode(data2.encode())
        pk1 = self.backend.packer.pack_pk(self.user.pk)
        pk2 = self.backend.packer.pack_pk(similar_user.pk)
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
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Bad token", self.get_log())


@override_settings(SESAME_MAX_AGE=10)
class TestModelBackendWithExpiry(TestModelBackend):
    @override_settings(SESAME_MAX_AGE=-10)
    def test_expired_token(self):
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Expired token", self.get_log())

    def test_token_without_timestamp(self):
        with override_settings(SESAME_MAX_AGE=None):
            token = ModelBackend().create_token(self.user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Valid signature but unexpected token", self.get_log())


@override_settings(SESAME_ONE_TIME=True)
class TestModelBackendWithOneTime(TestModelBackend):
    def test_no_last_login(self):
        self.user.last_login = None
        self.user.save()
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, self.user)
        self.assertIn("Valid token for user john", self.get_log())

    def test_last_login_change(self):
        token = self.backend.create_token(self.user)
        self.user.last_login = timezone.now() - datetime.timedelta(1800)
        self.user.save()
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Invalid token", self.get_log())


@override_settings(SESAME_INVALIDATE_ON_PASSWORD_CHANGE=False, SESAME_MAX_AGE=3600)
class TestModelBackendWithoutInvalidateOnPasswordChange(TestModelBackend):
    def test_password_change(self):
        token = self.backend.create_token(self.user)
        self.user.set_password("hunter2")
        self.user.save()
        user = self.backend.parse_token(token)
        self.assertEqual(user, self.user)
        self.assertIn("Valid token for user john", self.get_log())

    def test_insecure_configuration(self):
        with override_settings(SESAME_MAX_AGE=None):
            with self.assertRaises(ImproperlyConfigured) as exc:
                ModelBackend()
        self.assertEqual(
            str(exc.exception),
            "Insecure configuration: set SESAME_MAX_AGE to a low value "
            "or set SESAME_INVALIDATE_ON_PASSWORD_CHANGE to True",
        )


@override_settings(AUTH_USER_MODEL="test_app.BigAutoUser")
class TestModelBackendWithBigAutoPrimaryKey(TestModelBackend):

    pass


@override_settings(AUTH_USER_MODEL="test_app.UUIDUser")
class TestModelBackendWithUUIDPrimaryKey(TestModelBackend):

    pass


@override_settings(AUTH_USER_MODEL="test_app.BooleanUser")
class TestModelBackendWithUnsupportedPrimaryKey(TestCase):
    def setUp(self):
        self.backend = ModelBackend()

        User = get_user_model()
        self.user = User.objects.create(username=True)

    def test_authenticate(self):
        with self.assertRaises(NotImplementedError) as exc:
            self.backend.create_token(self.user)

        self.assertEqual(
            str(exc.exception), "BooleanField primary keys aren't supported",
        )
