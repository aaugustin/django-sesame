from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .utils import get_parameters, get_query_string, get_user


class TestUtils(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='john', password='doe')

    def test_get_parameters(self):
        self.assertEqual(list(get_parameters(self.user)), ['url_auth_token'])

    def test_get_query_string(self):
        self.assertIn('?url_auth_token=', get_query_string(self.user))

    def test_get_user(self):
        request = RequestFactory().get('/' + get_query_string(self.user))
        self.assertEqual(get_user(request), self.user)

    def test_get_user_no_token(self):
        request = RequestFactory().get('/')
        self.assertIsNone(get_user(request))
