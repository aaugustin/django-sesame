(In)security
============

.. warning::

    **Before using django-sesame in your project, please review the following
    advice carefully.** (Also, please don't use security-sensitive libraries
    published by strangers on the Internet without checking what they do.)

The major security weakness in django-sesame is a direct consequence of the
feature it implements: **whoever obtains an authentication token will be able
to authenticate to your website.**

URLs end up in countless insecure places: emails, referer headers, proxy logs,
browser history, etc. You can't avoid that. At best you can mitigate it by
creating short-lived or single-use tokens, as described below.

Otherwise, a reasonable attempt was made to provide a secure solution. Tokens
are secured with modern cryptography. There are configurable options for token
expiration and invalidation.
