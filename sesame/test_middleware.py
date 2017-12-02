from __future__ import unicode_literals

import io
import logging

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from .backends import ModelBackend


@override_settings(
    AUTHENTICATION_BACKENDS=[
        'django.contrib.auth.backends.ModelBackend',
        'sesame.backends.ModelBackend',
    ],
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'sesame.middleware.AuthenticationMiddleware',
    ],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                ],
            },
        },
    ],
)
class TestAfterAuthMiddleware(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='john', password='doe')
        self.token = ModelBackend().create_token(self.user)
        self.bad_token = self.token.lower()

        self.log = io.StringIO()
        self.handler = logging.StreamHandler(self.log)
        self.logger = logging.getLogger('sesame')
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    def test_token(self):
        response = self.client.get('/', {'url_auth_token': self.token})
        self.assertEqual(response.content, b'john')

    def test_bad_token(self):
        response = self.client.get('/', {'url_auth_token': self.bad_token})
        self.assertEqual(response.content, b'anonymous')

    def test_no_token(self):
        response = self.client.get('/')
        self.assertEqual(response.content, b'anonymous')


@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'sesame.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ],
)
class TestBeforeAuthMiddleware(TestAfterAuthMiddleware):
    pass


@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'sesame.middleware.AuthenticationMiddleware',
    ],
)
class TestWithoutAuthMiddleware(TestAfterAuthMiddleware):
    pass


@override_settings(
    MIDDLEWARE=[
        'sesame.middleware.AuthenticationMiddleware',
    ],
)
class TestWithoutSessionMiddleware(TestAfterAuthMiddleware):
    pass
