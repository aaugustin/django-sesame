from django.test import TestCase

from .backends import ModelBackend
from .test_mixins import CreateUserMixin
from .tokens import create_token


class TestModelBackend(CreateUserMixin, TestCase):
    def test_authenticate(self):
        token = create_token(self.user)
        user = ModelBackend().authenticate(request=None, url_auth_token=token)
        self.assertEqual(user, self.user)
