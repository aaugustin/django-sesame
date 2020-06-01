import logging

from . import settings

logger = logging.getLogger("sesame")

__all__ = ["create_token", "parse_token"]


def create_token(user):
    """
    Create a signed token for a user.

    """
    tokens = settings.TOKENS[0]
    return tokens.create_token(user)


def parse_token(token, get_user):
    """
    Obtain a user from a signed token.

    """
    for tokens in settings.TOKENS:
        # We can detect the version of a token simply by inspecting it:
        # v1 tokens contain a colon; v2 tokens don't.
        if tokens.detect_token(token):
            return tokens.parse_token(token, get_user)
    else:
        logger.debug("Bad token: doesn't match a supported format")
        return
