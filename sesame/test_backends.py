from __future__ import unicode_literals

import io
import logging

from django.contrib.auth.models import User
from django.test import TestCase

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
        user = self.backend.authenticate(url_auth_token=token)
        self.assertEqual(user, self.user)

    def test_token(self):
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token)
        self.assertEqual(user, self.user)
        self.assertIn("Valid token for user john", self.get_log())

    def test_invalid_token(self):
        token = self.backend.create_token(self.user)
        user = self.backend.parse_token(token.lower())
        self.assertEqual(user, None)
        self.assertIn("Invalid token", self.get_log())

    def test_unknown_token(self):
        token = self.backend.create_token(self.user)
        self.user.delete()
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Unknown token", self.get_log())

    def test_expired_token(self):
        token = self.backend.create_token(self.user)
        self.user.set_password('hunter2')
        self.user.save()
        user = self.backend.parse_token(token)
        self.assertEqual(user, None)
        self.assertIn("Expired token", self.get_log())

    def test_type_error_is_logged(self):
        def raise_type_error(*args):
            raise TypeError
        self.backend.parse_token = raise_type_error
        with self.assertRaises(TypeError):
            self.backend.authenticate(None)
        self.assertIn("TypeError", self.get_log())
