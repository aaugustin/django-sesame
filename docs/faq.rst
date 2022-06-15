Frequent questions
==================

How do I understand why a token is invalid?
-------------------------------------------

Enable debug logs by setting the ``sesame`` logger to the ``DEBUG`` level.

.. code-block:: python

    import logging
    logger = logging.getLogger("sesame")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

Then you should get a hint in logs.

Depending on how logging is set up in your project, there may by another way
to enable this configuration.

Why does upgrading Django invalidate tokens?
--------------------------------------------

As a security measure, django-sesame invalidates tokens when users change their
password.

Each release of Django increases the work factor of password hashers. After
deploying a new version of Django, when a user logs in with their password,
Django upgrades the password hash.

From the perspective of django-sesame, this is indistinguishable from changing
their password.

Indeed, by design, django-sesame relies exclusively on data available in the
user model: ``pk``, ``password`` (hashed), and ``last_login``. When ``password``
changes, django-sesame cannot tell if the password was changed or if the hash
was upgraded.

That's how tokens become invalid.

This problem occurs only when a user logs in alternatively with a long-lived
token and with a password. If you're in this situation, you should regenerate
and redistribute tokens after upgrading Django.

Alternatively, you may set :data:`SESAME_INVALIDATE_ON_PASSWORD_CHANGE` to
:obj:`False` to disable token invalidation on password change. Think through
security ramifications before doing this, especially if tokens are long lived.

Why do all tokens start with AAAA...?
-------------------------------------

This is the Base64 encoding of an integer storing a small value.

By default, Django uses integers as primary keys for users, starting from 1.
These primary keys are included in tokens, which are encoded with Base64.

When the primary key of the user model is an
:class:`~django.db.models.AutoField`, as long as you have less that one million
users, all tokens start with AA.

Why do one-time tokens sent by email fail?
------------------------------------------

Email providers may fetch links found emails to provide previews or for security
purposes. If the link contains a one-time token, this will invalidate the token.

To avoid this, you can configure a short :data:`SESAME_MAX_AGE` instead of
enabling :data:`SESAME_ONE_TIME`.

Is django-sesame usable without passwords?
------------------------------------------

Yes, it is.

You should call :meth:`~django.contrib.auth.models.User.set_unusable_password`
when you create users.

Is django-sesame compatible with custom user models?
----------------------------------------------------

Yes, it is.

It requires ``password`` and ``last_login`` fields. These are provided by
:class:`~django.contrib.auth.models.AbstractBaseUser`, the recommended base
class for custom user models.

Is django-sesame compatible with Django REST framework?
-------------------------------------------------------

Yes, it is.

However, you should favor Django REST framework's built-in
|TokenAuthentication|__ or recommended alternatives.

.. |TokenAuthentication| replace:: ``TokenAuthentication``
__ https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
