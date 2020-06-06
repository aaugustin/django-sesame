.. image:: logo/horizontal.svg
   :width: 400px
   :alt: django-sesame

#############
django-sesame
#############

`django-sesame`_ provides frictionless authentication with "Magic Links" for
your Django project.

.. _django-sesame: https://github.com/aaugustin/django-sesame

It generates URLs containing authentication tokens such as:
https://example.com/?sesame=zxST9d0XT9xgfYLvoa9e2myN

Then it authenticates users based on tokens found in URLs.

Table of contents
=================

* `Use cases`_
* `(In)security`_
* `User guide`_

  * `Requirements`_
  * `Getting started`_
  * `Generating URLs`_
  * `Tokens lifecycle`_
  * `Per-view authentication`_

* `Advanced topics`_

  * `Safari issues`_
  * `Tokens security`_
  * `Custom primary keys`_
  * `Stateless authentication`_

* `Infrequently asked questions`_
* `Contributing`_
* `Changelog`_

Use cases
=========

Known use cases for django-sesame include:

1. Login by email, an increasingly attractive option on mobile where
   typing passwords is uncomfortable. This technique is prominently
   deployed by Slack.

   If you're doing this, you should define a small ``SESAME_MAX_AGE``, perhaps
   10 minutes.

2. Authenticated links, typically if you're generating a report offline, then
   emailing a link to access it when it's ready. An authenticated link works
   even if the user isn't logged in on the device where they're opening it.

   Likewise, you should configure an appropriate ``SESAME_MAX_AGE``, probably
   no more than a few days.

   Since emails may be forwarded, authenticated links shouldn't log the user
   in. They should only allow access to specific views, as described in
   `Per-view authentication`_.

3. Sharing links, which are a variant of authenticated links. When a user
   shares content with a guest, you can create a phantom account for the guest
   and generate an authenticated link tied to that account.

   Email forwarding is even more likely in this context. If you're doing this,
   make sure authenticated links don't log the user in.

4. Non-critical private websites, for example for a family or club site,
   where users don't expect to manage a personal account with a password.
   Authorized users can bookmark personalized authenticated URLs.

   Here you can rely on the default settings because that's the original —
   and, admittedly, niche — use case for which django-sesame was built.

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

User guide
==========

Requirements
------------

django-sesame is tested with:

- Django 2.2 (LTS) and 3.0;
- Python ≥ 3.6

It builds upon ``django.contrib.auth``. It supports custom user models,
provided they have ``password`` and ``last_login`` fields. Most custom user
models inherit these fields from ``AbstractBaseUser``.

django-sesame is released under the BSD license, like Django itself.

Getting started
---------------

1. Install django-sesame:

   .. code:: bash

    $ pip install django-sesame[ua]

   The ``ua`` extra is optional. See `Safari issues`_ for details.

2. Add ``"sesame.backends.ModelBackend"`` to ``AUTHENTICATION_BACKENDS``:

   .. code:: python

    AUTHENTICATION_BACKENDS += ["sesame.backends.ModelBackend"]

3. Add ``"sesame.middleware.AuthenticationMiddleware"`` to ``MIDDLEWARE``:

   .. code:: python

    MIDDLEWARE += ["sesame.middleware.AuthenticationMiddleware"]

   The best position for ``sesame.middleware.AuthenticationMiddleware`` is
   just after ``django.contrib.auth.middleware.AuthenticationMiddleware``.

Generating URLs
---------------

django-sesame provides functions to generate authenticated URLs in the
``sesame.utils`` module.

Load a user from the database:

.. code:: python

    >>> from django.contrib.auth import get_user_model
    >>> User = get_user_model()
    >>> user = User.objects.first()

Now you can create a query string that you can append to any URL to enable
one-click login:

.. code:: python

    >>> from sesame.utils import get_query_string
    >>> get_query_string(user)
    '?sesame=zxST9d0XT9xgfYLvoa9e2myN'

You can also obtain a ``dict`` of parameters rather than ready-to-use query
string:

.. code:: python

    >>> from sesame.utils import get_parameters
    >>> get_parameters(user)
    {'sesame': 'zxST9d0XT9xgfYLvoa9e2myN'}

Then you can add other parameters to this ``dict`` before serializing it to a
query string.

Finally, here's how to get only the token:

.. code:: python

    >>> from sesame.utils import get_token
    >>> get_token(user)
    'zxST9d0XT9xgfYLvoa9e2myN'

Share the resulting URLs with your users though an adequately confidential
channel for your use case.

By default, the URL parameter is named ``sesame``. You can change this with
the ``SESAME_TOKEN_NAME`` setting. Make sure that it doesn't conflict with
other query string parameters used by your application.

*Changed in 2.0:* the URL parameter used to be named ``url_auth_token``.

Tokens lifecycle
----------------

By default, tokens don't expire but are tied to the password of the user.
Changing the password invalidates the token. When the authentication backend
uses salted passwords — that's been the default in Django for a long time —
the token is invalidated even if the new password is identical to the old one.

If you want tokens to expire after a given amount of time, set the
``SESAME_MAX_AGE`` setting to a duration in seconds or a
``datetime.timedelta``. Then each token will contain the time it was generated
at and django-sesame will check if it's still valid at each login attempt.

If you want tokens to be usable only once, set the ``SESAME_ONE_TIME`` setting
to ``True``. Then tokens are valid only if the last login date hasn't changed
since they were generated. Since logging in changes the last login date, such
tokens are usable at most once. If you're intending to send links by email, be
aware that some email providers scan links for security reasons, which
consumes single-use tokens prematurely. Tokens with a short expiry are more
reliable.

If you don't want tokens to be invalidated by password changes, set the
``SESAME_INVALIDATE_ON_PASSWORD_CHANGE`` setting to ``False``. **This is
discouraged because it becomes impossible to invalidate a single token.** Your
only option if a token is compromised is to invalidate all tokens at once. If
you're doing it anyway, you should set ``SESAME_MAX_AGE`` to a short value to
minimize risks. This option may be useful for generating tokens during a
sign up process, when you don't know if the token will be used before or after
initializing the password.

Finally, if the ``is_active`` attribute of a user is set to ``False``,
django-sesame rejects authentication tokens for this user.

Tokens must be verified with the same settings that were used for generating
them. Changing settings invalidates previously generated tokens. The only
exception to this rule is ``SESAME_MAX_AGE``: as long as it isn't ``None``,
you can change its value and the new value will apply even to previously
generated tokens.

Per-view authentication
-----------------------

The configuration described in `Getting started`_ enables a middleware that
looks for a token in every request and, if there is a valid token, logs the
user in. It's as if they had submitted their username and password in a login
form. This provides compatibility with APIs like the ``login_required``
decorator and the ``LoginRequired`` mixin.

Sometimes this behavior is too blunt. For example, you may want to build a
Magic Link that gives access to a specific view but doesn't log the user in
permanently.

To achieve this, remove ``"sesame.middleware.AuthenticationMiddleware"`` from
the ``MIDDLEWARE`` setting and authenticate the user with django-sesame in a
view as follows:

.. code:: python

    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse

    from sesame.utils import get_user

    def hello(request):
        user = get_user(request)
        if user is None:
            raise PermissionDenied
        return HttpResponse("Hello {}!".format(user))

When ``get_user()`` returns ``None``, it means that the token was missing,
invalid, expired, or that the user account is inactive. Then you can show an
appropriate error message or redirect to a login form.

When ``SESAME_ONE_TIME`` is enabled, ``get_user()`` updates the user's last
login date in order to invalidate the token. When ``SESAME_ONE_TIME`` isn't
enabled, it doesn't, because making a database write for every call to
``get_user()`` could degrade performance. You can override this behavior with
the ``update_last_login`` keyword argument:

.. code:: python

    get_user(request, update_last_login=True)   # always update last_login
    get_user(request, update_last_login=False)  # never update last_login

``get_user()`` is a thin wrapper around the low-level ``authenticate()``
function from ``django.contrib.auth``. It's also possible to verify an
authentication token directly with  ``authenticate()``. To do so, the
``sesame.backends.ModelBackend`` authentication backend expects an
``sesame`` argument:

.. code:: python

    from django.contrib.auth import authenticate

    user = authenticate(sesame=...)

*Changed in 2.0:* the argument used to be named ``url_auth_token``.

If you decide to use ``authenticate()`` instead of ``get_user()``, you must
update ``user.last_login`` to invalidate one-time tokens. Indeed, in
``django.contrib.auth``, ``authenticate()`` is a low-level function. The
caller, usually the higher-level ``login()`` function, is responsible for
updating ``user.last_login``.

Advanced topics
===============

Safari issues
-------------

The django-sesame middleware removes the token from the URL with a HTTP 302
Redirect after authenticating a user successfully. Unfortunately, in some
scenarios, this triggers Safari's "Protection Against First Party Bounce
Trackers". In that case, Safari clears cookies and the user is logged out.

To avoid this problem, django-sesame doesn't perform the redirect when it
detects that the browser is Safari. This relies on the ua-parser package,
which is an optional dependency. If it isn't installed, django-sesame always
redirects.

Tokens security
---------------

django-sesame builds authentication tokens as follows:

- Encode the primary key of the user for which they were generated;
- Assemble a revocation key which will be used for invalidating tokens;
- If ``SESAME_MAX_AGE`` is enabled, encode the token generation timestamp;
- Add a message authentication code (MAC) to prevent tampering with the token.

The revocation key is derived from:

- The password of the user, unless ``SESAME_INVALIDATE_ON_PASSWORD_CHANGE`` is
  disabled;
- The last login date of the user, if ``SESAME_ONE_TIME`` is enabled.

Primary keys are in clear text. If this is a concern, you can write a custom
packer to encrypt them. See `Custom primary keys`_ for details.

django-sesame provides two token formats:

- v1 is the original format, which still works as designed;
- v2 is a better, cleaner, faster design that produces shorter tokens.

The ``SESAME_TOKENS`` setting lists supported formats in order of decreasing
preference. The first item defines the format of newly created tokens. Other
items define other acceptable formats, if any.

``SESAME_TOKENS`` defaults to ``["sesame.tokens_v2", "sesame.tokens_v1"]``
which means "generate tokens v2, accept tokens v2 and v1".

Tokens v2
.........

They contain a primary key, an optional timestamp, and a signature.

The signature covers the primary key, the optional timestamp, and the
revocation key. If the revocation key changes, the signature becomes invalid.
As a consequence, there's no need to include the revocation key in tokens.

The signature algorithm is Blake2 in keyed mode. A unique key is derived by
hashing the ``SECRET_KEY`` setting and relevant ``SESAME_*`` settings.

By default the signature length is 10 bytes. You can adjust it to any value
between 1 and 64 bytes with the ``SESAME_SIGNATURE_SIZE`` setting.

If you need to invalidate all tokens, set the ``SESAME_KEY`` setting to a new
value. This will change the unique key and, as a consequence, invalidate all
signatures.

Tokens v1
.........

Tokens v1 contain a primary key and a revocation key, plus an optional
timestamp and a signature generated by Django's built-in ``Signer`` or
``TimestampSigner``.

The signature algorithm HMAC-SHA1.

If you need to invalidate all tokens, you can set the ``SESAME_SALT`` setting
to a new value. This will change all signatures.

Custom primary keys
-------------------

When generating a token for a user, django-sesame stores the primary key of
that user in the token. In order to keep tokens short, django-sesame creates
compact binary representations of primary keys, according to their type.

If you're using integer or UUID primary keys, you're fine. If you're using
another type of primary key, for example a string created by a unique ID
generation algorithm, the default representation may be suboptimal.

For example, let's say primary keys are strings containing 24 hexadecimal
characters. The default packer represents them with 25 bytes. You can reduce
them to 12 bytes with this custom packer:

.. code:: python

    from sesame.packers import BasePacker

    class Packer(BasePacker):

        @staticmethod
        def pack_pk(user_pk):
            assert len(user_pk) == 24
            return bytes.fromhex(user_pk)

        @staticmethod
        def unpack_pk(data):
            return data[:12].hex(), data[12:]

Then, set the ``SESAME_PACKER`` setting to the dotted Python path to your
custom packer class.

For details, read ``help(BasePacker)`` and look at built-in packers defined in
the ``sesame.packers`` module.

Stateless authentication
------------------------

Theoretically, django-sesame can provide stateless authenticated navigation
without ``django.contrib.sessions``, provided all internal links include the
authentication token. That increases the security concerns and it's unclear
that it meets any practical use case.

In a scenario where ``django.contrib.sessions.middleware.SessionMiddleware``
and ``django.contrib.auth.middleware.AuthenticationMiddleware`` aren't
enabled, ``sesame.middleware.AuthenticationMiddleware`` still sets
``request.user`` to the currently logged-in user or ``AnonymousUser()``.

Infrequently asked questions
============================

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

Contributing
============

Prepare a development environment:

* Install Poetry_.
* Run ``poetry install --extras ua``.
* Run ``poetry shell`` to load the development environment.

Make changes:

* Make changes to the code, tests, or docs.
* Run ``make style`` and fix any flake8 violations.
* Run ``make test`` or ``make coverage`` to run the set suite — it's fast!

Iterate until you're happy.

Check quality and submit your changes:

* Install tox_.
* Run ``tox`` to test across Python and Django versions — it's quite slow.
* Submit a pull request.

.. _Poetry: https://python-poetry.org/
.. _tox: https://tox.readthedocs.io/

Changelog
=========

2.0
---

* Introduced a faster and shorter token format (v2). The previous format (v1)
  is still supported. See `Tokens security`_.
* Added the ``get_token()`` function to generate a token.
* **Backwards-incompatible** Changed the default URL parameter to ``sesame``.
  If you need to preserve existing URLs, you can set
  ``SESAME_TOKEN_NAME = "url_auth_token"``.
* **Backwards-incompatible** Changed the argument expected by
  ``authenticate()`` to ``sesame``. You're affected only if you're explicitly
  calling ``authenticate(url_auth_token=...)``. If so, change this call to
  ``authenticate(sesame=...)``.
* ``SESAME_MAX_AGE`` can be a ``datetime.timedelta``.
* Improved documentation.

1.8
---

* Added compatibility with custom user models with most types of primary keys,
  including ``BigAutoField``, ``SmallAutoField``, other integer fields,
  ``CharField`` and ``BinaryField``.
* Added the ability to customize how primary keys are stored in tokens.
* Added compatibility with Django ≥ 3.0.

1.7
---

* Fixed invalidation of one-time tokens in ``get_user()``.

1.6
---

* Fixed detection of Safari on iOS.

1.5
---

* Added support for single use tokens with the ``SESAME_ONE_TIME`` setting.
* Added support for not invalidating tokens on password change with the
  ``SESAME_INVALIDATE_ON_PASSWORD_CHANGE`` setting.
* Added compatibility with custom user models where the primary key is a
  ``UUIDField``.
* Added the ``get_user()`` function to obtain a user instance from a request.
* Improved error message for preexisting tokens when changing the
  ``SESAME_MAX_AGE`` setting.
* Fixed authentication on Safari by disabling the redirect which triggers ITP.

1.4
---

* Added a redirect to the same URL with the query string parameter removed.

1.3
---

* Added compatibility with Django ≥ 2.0.

1.2
---

* Added the ability to rename the query string parameter with the
  ``SESAME_TOKEN_NAME`` setting.
* Added compatibility with Django ≥ 1.8.

1.1
---

* Added support for expiring tokens with the ``SESAME_MAX_AGE`` setting.

1.0
---

* Initial release.
