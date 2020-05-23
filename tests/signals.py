from django.core.signals import setting_changed
from django.dispatch import receiver

from sesame import settings, tokens


@receiver(setting_changed)
def reset_sesame_settings(**kwargs):
    settings.load()
    tokens.signer = tokens.get_signer()
    tokens.packer = tokens.get_packer()
