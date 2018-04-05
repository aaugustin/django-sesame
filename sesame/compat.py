try:
    from urllib.parse import urlencode  # noqa: F401
except ImportError:
    from urllib import urlencode  # noqa: F401
