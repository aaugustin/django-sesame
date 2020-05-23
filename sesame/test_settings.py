from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.dispatch import receiver
from django.test import TestCase, override_settings

from . import settings, tokens


@receiver(setting_changed)
def reset_sesame_settings(**kwargs):
    settings.load()
    tokens.signer = tokens.get_signer()
    tokens.packer = tokens.get_packer()


class TestSettings(TestCase):
    @override_settings(SESAME_INVALIDATE_ON_PASSWORD_CHANGE=False, SESAME_MAX_AGE=None)
    def test_insecure_configuration(self):
        with self.assertRaises(ImproperlyConfigured) as exc:
            settings.check()
        self.assertEqual(
            str(exc.exception),
            "Insecure configuration: set SESAME_MAX_AGE to a low value "
            "or set SESAME_INVALIDATE_ON_PASSWORD_CHANGE to True",
        )
