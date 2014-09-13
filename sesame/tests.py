from __future__ import unicode_literals

import django

if django.VERSION[:2] < (1, 6):     # unittest-style discovery isn't available
    from .test_backends import TestModelBackend                         # noqa
    from .test_middleware import TestAfterAuthMiddleware                # noqa
    from .test_middleware import TestBeforeAuthMiddleware               # noqa
    from .test_middleware import TestWithoutAuthMiddleware              # noqa
    from .test_middleware import TestWithoutSessionMiddleware           # noqa
    from .test_utils import TestUtils                                   # noqa
