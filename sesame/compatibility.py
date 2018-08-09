import sys
try:
    if sys.version_info >= (3, 0):
        from urllib.parse import urlencode                      # noqa: F401
    else:
        from urllib import urlencode                            # noqa: F401
except ImportError:                                         # pragma: no cover
    from urllib import urlencode                            # noqa: F401
