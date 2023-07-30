Changelog
=========

3.2
---

*July 30th, 2023*

* Added support for invalidating tokens on email change with the
  :data:`SESAME_INVALIDATE_ON_EMAIL_CHANGE` setting.
* Supported overriding settings for testing.

3.1
---

*July 28th, 2022*

* Added the ability to select which field is used as a primary key in tokens
  with the :data:`SESAME_PRIMARY_KEY_FIELD` setting.
* Supported the ``SECRET_KEY_FALLBACKS`` setting introduced in Django 4.1.

3.0
---

*July 11th, 2022*

.. admonition:: Version 3.0 introduces a new documentation.
    :class: important

    Notably, a :ref:`tutorial <Tutorial>` and an :ref:`API reference` were
    added.

.. admonition:: Enforced ``update_last_login`` as a keyword-only argument in
        :func:`~sesame.utils.get_user`.
    :class: warning

    ``update_last_login`` was documented as a keyword argument. However, it
    could also be the first positional argument. If you were doing this, you
    will hit an exception.

Also:

* Added :func:`~sesame.decorators.authenticate` to authenticate users.
* Added :class:`~sesame.views.LoginView` to log users in.
* Added compatibility with Django ≥ 4.0.

2.4
---

*May 5th, 2021*

* Added the ability to pass a token to :func:`~sesame.utils.get_user` instead of
  a request.

2.3
---

*February 15th, 2021*

* Supported overriding ``max_age``. This feature is only available for v2 tokens.

2.2
---

*January 16th, 2021*

* Fixed crash when a v2 token is truncated.

2.1
---

*November 1st, 2020*

* Added :ref:`scoped tokens <Scoped tokens>`. This feature is only available for
  v2 tokens.

2.0
---

*June 6th, 2020*

.. admonition:: Version 2.0 introduces a faster and shorter token format (v2).
    :class: important

    The new format (v2) is enabled by default for new tokens.

    The original format (v1) is still supported for backwards-compatibility.

    See :ref:`Tokens design` for details.

.. admonition:: Changed the default name of the URL parameter to ``sesame``.
    :class: warning

    If you need to preserve existing URLs, you can set the
    :data:`SESAME_TOKEN_NAME` setting ``"url_auth_token"``.

.. admonition:: Changed the argument expected by
        :func:`~django.contrib.auth.authenticate` to ``sesame``.
    :class: warning

    You're affected only if you call ``authenticate(url_auth_token=...)``
    explicitly. If so, change this call to ``authenticate(sesame=...)``.

Also:

* Added :func:`~sesame.utils.get_token()` to generate a token.
* :data:`SESAME_MAX_AGE` can be a :class:`datetime.timedelta`.
* Improved documentation.

1.8
---

*May 11th, 2020*

* Added compatibility with custom user models with most types of primary keys,
  including :class:`~django.db.models.BigAutoField`,
  :class:`~django.db.models.SmallAutoField`, other integer fields,
  :class:`~django.db.models.CharField`, and
  :class:`~django.db.models.BinaryField`.
* Added the ability to customize how primary keys are stored in tokens with the
  :data:`SESAME_PACKER` setting.
* Added compatibility with Django ≥ 3.0.

1.7
---

*June 8th, 2019*

* Fixed invalidation of one-time tokens in :func:`~sesame.utils.get_user`.

1.6
---

*May 18th, 2019*

* Fixed detection of Safari on iOS.

1.5
---

*May 1st, 2019*

* Added support for single-use tokens with the :data:`SESAME_ONE_TIME` setting.
* Added support for not invalidating tokens on password change with the
  :data:`SESAME_INVALIDATE_ON_PASSWORD_CHANGE` setting.
* Added compatibility with custom user models where the primary key is a
  :class:`~django.db.models.UUIDField`.
* Added the :func:`~sesame.utils.get_user` function to obtain a user instance
  from a request.
* Improved error message for preexisting tokens when changing the
  :data:`SESAME_MAX_AGE` setting.
* Fixed authentication on Safari by :ref:`disabling redirect <Safari issues>`.

1.4
---

*April 29th, 2018*

* Added a redirect to the same URL with the query string parameter removed.

1.3
---

*December 2nd, 2017*

* Added compatibility with Django ≥ 2.0.

1.2
---

*August 19th, 2016*

* Added the ability to rename the query string parameter with the
  :data:`SESAME_TOKEN_NAME` setting.
* Added compatibility with Django ≥ 1.8.

1.1
---

*September 17th, 2014*

* Added support for expiring tokens with the :data:`SESAME_MAX_AGE` setting.

1.0
---

*July 3rd, 2014*

* Initial release.
