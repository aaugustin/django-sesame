from django.contrib.auth.models import User
from django.test import TestCase

from sesame.utils import get_parameters, get_query_string


class TestUtils(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='john', password='doe')

    def test_get_parameters(self):
        self.assertEqual(get_parameters(self.user).keys(), ['url_auth_token'])

    def test_get_query_string(self):
        self.assertIn('?url_auth_token=', get_query_string(self.user))
