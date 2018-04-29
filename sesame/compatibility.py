try:
    from urllib.parse import urlencode                      # noqa: F401
except ImportError:                                         # pragma: no cover
    from urllib import urlencode                            # noqa: F401
