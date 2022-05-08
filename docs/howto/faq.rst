(In)frequently asked questions
==============================

**Is django-sesame usable without passwords?**

Yes, it is.

You should call ``user.set_unusable_password()`` when you create users.

**How do I understand why a token is invalid?**

Enable debug logs by setting the ``sesame`` logger to the ``DEBUG`` level.

.. code:: python

    import logging
    logger = logging.getLogger("sesame")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

Then you should get a hint in logs.

Depending on how logging is set up in your project, there may by another way
to enable this configuration.

**Why does upgrading Django invalidate tokens?**

Each release of Django increases the work factor of password hashers. After
deploying a new version of Django, when a user logs in with their password,
Django upgrades the password hash. This invalidates the user's token.

This problem occurs only when a user logs in alternatively with a long-lived
token and with a password, which isn't frequent in practice. If you're facing
it, you should regenerate and redistribute tokens after upgrading Django.

Other workarounds, such as disabling token invalidation on password change or
using a custom hasher to keep the work factor constant, are discouraged
because they create security concerns.

**Why do all tokens start with AAAA...?**

This is the Base64 encoding of an integer storing a small value.

By default, Django uses integers as primary keys for users, starting from 1.
These primary keys are included in tokens, which are encoded with Base64.

When the primary key of the ``User`` model is an ``AutoField``, as long as you
have less that one million users, all tokens start with AA.
