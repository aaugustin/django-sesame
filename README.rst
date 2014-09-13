django-sesame
#############

Introduction
============

`django-sesame`_ provides one-click login for your Django project. It uses
specially crafted URLs containing an authentication token, for example:
http://example.com/?url_auth_token=AAAAARchl18CIQUlImmbV9q7PZk%3A89AEU34b0JLSrkT8Ty2RPISio5

It's useful if you want to share private content without requiring your visitors
to remember a username and a password.

django-sesame is tested with:

- Django 1.4 (LTS), 1.6 and 1.7,
- all supported Python versions (except Python 2.5 for Django 1.4).

It's tied to ``django.contrib.auth``. It uses ``django.contrib.session`` when
it's available, but it also supports stateless authenticated navigation,
provided all links in the page include the authentication token.

django-sesame is released under the BSD license, like Django itself.

.. _django-sesame: https://github.com/aaugustin/django-sesame

A few words about security
==========================

**Before using django-sesame in your project, you should review the following
advice carefully.**

The major security weakness in django-sesame is a direct consequence of the
feature it implements: **whoever obtains an authentication token will be able to
log in to your website.** URLs end up in countless insecure places: browser
history, proxy logs, etc. You can't avoid that. So use django-sesame only for
mundane things, like photos from your holidays. If a data leak would seriously
affect you, don't use this software. You have been warned.

Otherwise, a reasonable attempt has been made to provide a secure solution.
django-sesame uses Django's signing framework to create signed tokens.

Tokens are linked to the primary key of the ``User`` object and they never
expire. However changing the user's password invalidates his token. Provided
your authentication backend uses salted passwords — I hope it does — the token
is invalidated even if the new password is identical to the old one.

If you want a more advanced logic, like timed expiration, you should subclass
``sesame.backends.ModelBackend``.

How to
======

1.  Add ``sesame.backends.ModelBackend`` to ``AUTHENTICATION_BACKENDS``::

        AUTHENTICATION_BACKENDS += 'sesame.backends.ModelBackend',

2.  Add ``sesame.middleware.AuthenticationMiddleware`` to ``MIDDLEWARE_CLASSES``::

        MIDDLEWARE_CLASSES += 'sesame.middleware.AuthenticationMiddleware',

3. Generate authentication tokens with ``sesame.utils.get_query_string(user)``.

That's all!

Utilities
=========

``sesame.utils`` provides two simple functions to generate authentication
tokens. ``get_query_string(user)`` returns a complete query string that you can
append to any URL to enable one-click login. If you already have a query string,
``get_parameters(user)`` returns a dictionary of additional GET parameters to
include.
