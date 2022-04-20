import datetime
import io
import logging
import unittest

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone


class CreateUserMixin(TestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user()

    def create_user(self, username="john", password="letmein", **kwargs):
        User = get_user_model()
        user = User(
            username=username,
            last_login=timezone.now() - datetime.timedelta(seconds=3600),
            **kwargs,
        )
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def get_user(user_id):
        return get_user_model().objects.filter(pk=user_id).first()

    @staticmethod
    def get_custom_user(user_key):
        return get_user_model().objects.filter(id=user_key).first()


class CaptureLogMixin(unittest.TestCase):

    logger_name = "sesame"

    def setUp(self):
        super().setUp()
        self.buffer = io.StringIO()
        self.handler = logging.StreamHandler(self.buffer)
        self.logger = logging.getLogger(self.logger_name)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    @property
    def logs(self):
        self.handler.flush()
        return self.buffer.getvalue()

    def assertNoLogs(self):
        self.assertEqual(self.logs, "")

    def assertLogsContain(self, message):
        self.assertIn(message, self.logs)

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        super().tearDown()
