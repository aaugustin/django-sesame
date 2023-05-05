import datetime

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from sesame import settings

from .signals import reset_sesame_settings  # noqa


class TestSettings(TestCase):
    @override_settings(SESAME_MAX_AGE=datetime.timedelta(minutes=5))
    def test_max_age_timedelta(self):
        self.assertEqual(settings.MAX_AGE, 300)

    @override_settings(
        SESAME_INVALIDATE_ON_PASSWORD_CHANGE=False,
        SESAME_MAX_AGE=None,
    )
    def test_insecure_configuration(self):
        with self.assertRaises(ImproperlyConfigured) as exc:
            settings.check()
        self.assertEqual(
            str(exc.exception),
            "insecure configuration: set SESAME_MAX_AGE to a low value "
            "or set SESAME_INVALIDATE_ON_PASSWORD_CHANGE to True",
        )

    @override_settings(
        SESAME_INVALIDATE_ON_EMAIL_CHANGE=False,
        AUTH_USER_MODEL="tests.StrUser",
    )
    def test_invalid_configuration(self):
        with self.assertRaises(ImproperlyConfigured) as exc:
            settings.check()
        self.assertEqual(
            str(exc.exception),
            "invalid configuration: set User.EMAIL_FIELD correctly "
            "or set SESAME_INVALIDATE_ON_EMAIL_CHANGE to False",
        )
