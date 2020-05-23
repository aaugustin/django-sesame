import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .backends import ModelBackend
from .tokens import create_token


class TestModelBackend(TestCase):

    username =  "john"

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(
            username=self.username,
            last_login=timezone.now() - datetime.timedelta(3600),
        )

    def test_authenticate(self):
        token = create_token(self.user)
        user = ModelBackend().authenticate(request=None, url_auth_token=token)
        self.assertEqual(user, self.user)
