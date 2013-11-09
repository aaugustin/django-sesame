from __future__ import unicode_literals

import django

if django.VERSION[:2] < (1, 6):     # unittest-style discovery isn't available
    from .test_backends import TestModelBackend
    from .test_middleware import TestAfterAuthMiddleware
    from .test_middleware import TestBeforeAuthMiddleware
    from .test_middleware import TestWithoutAuthMiddleware
    from .test_middleware import TestWithoutSessionMiddleware
    from .test_utils import TestUtils
