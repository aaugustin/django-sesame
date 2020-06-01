from django.core.signals import setting_changed
from django.dispatch import receiver

from sesame import packers, settings, tokens_v1


@receiver(setting_changed)
def reset_sesame_settings(**kwargs):
    settings.load()
    tokens_v1.signer = tokens_v1.get_signer()
    tokens_v1.token_re = tokens_v1.get_token_re()
    packers.packer = packers.get_packer()
