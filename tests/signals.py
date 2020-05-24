from django.core.signals import setting_changed
from django.dispatch import receiver

from sesame import packers, settings, tokens


@receiver(setting_changed)
def reset_sesame_settings(**kwargs):
    settings.load()
    tokens.signer = tokens.get_signer()
    packers.packer = packers.get_packer()
