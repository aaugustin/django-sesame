from __future__ import unicode_literals

import datetime
import io
import logging

from django.contrib.auth import get_user_model
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

    def test_type_error_is_logged(self):
        def raise_type_error(*args):
            raise TypeError

        self.backend.parse_token = raise_type_error
        with self.assertRaises(TypeError):
            self.backend.authenticate(request=None, url_auth_token=None)
        self.assertIn("TypeError", self.get_log())


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


@override_settings(AUTH_USER_MODEL="test_app.UUIDUser")
class TestModelBackendWithUUIDPrimaryKey(TestModelBackend):

    pass


@override_settings(AUTH_USER_MODEL="test_app.CharUser")
class TestModelBackendWithUnsupportedPrimaryKey(TestCase):
    def setUp(self):
        self.backend = ModelBackend()

        User = get_user_model()
        self.user = User.objects.create(username="john")

    def test_authenticate(self):
        with self.assertRaises(NotImplementedError) as exc:
            self.backend.create_token(self.user)

        self.assertEqual(
            str(exc.exception), "CharField primary keys aren't supported at this time"
        )
