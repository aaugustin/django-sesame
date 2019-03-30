from __future__ import unicode_literals

import io
import logging
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .backends import ModelBackend


class TestModelBackend(TestCase):

    def setUp(self):
        self.backend = ModelBackend()
        self.user = User.objects.create_user(username='john', password='doe')

        self.log = io.StringIO()
        self.handler = logging.StreamHandler(self.log)
        self.logger = logging.getLogger('sesame')
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

    def test_token(self):
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, self.user)
        self.assertIn("Valid token for user john", self.get_log())

    def test_bad_token(self):
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token.lower())
        self.assertEqual(user, None)
        self.assertIn("Bad token", self.get_log())

    def test_unknown_token(self):
        token = self.backend.create_token(self.user)
        self.user.delete()
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Unknown token", self.get_log())

    def test_invalid_token(self):
        token = self.backend.create_token(self.user)
        self.user.set_password('hunter2')
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


class TestModelBackendWithExpiry(TestModelBackend):

    def setUp(self):
        super(TestModelBackendWithExpiry, self).setUp()
        self.backend.max_age = 10                   # override class variable

    def test_expired_token(self):
        self.backend.max_age = -10                  # just for this test

        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Expired token", self.get_log())


class TestModelBackendWithOneTime(TestModelBackend):

    def setUp(self):
        super(TestModelBackendWithOneTime, self).setUp()
        self.login_user = User.objects.create_user(
            username='jane',
            password='doe',
            last_login=timezone.now() - timedelta(1),
            )
        self.backend.one_time = True                # override class variable

    def test_authenticate(self):
        token = self.backend.create_token(self.login_user)
        user = self.backend.authenticate(request=None, url_auth_token=token)
        self.assertEqual(user, self.login_user)

    def test_token(self):
        token = self.backend.create_token(self.login_user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, self.login_user)
        self.assertIn("Valid token for user jane", self.get_log())

    def test_token_last_login_none(self):
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, self.user)
        self.assertIn("Valid token for user john", self.get_log())

    def test_invalid_token(self):
        token = self.backend.create_token(self.user)
        self.user.last_login = timezone.now()
        self.user.save()
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Invalid token", self.get_log())
