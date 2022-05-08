Changelog
=========

2.4
---

* Added the ability to pass a token to ``get_user()`` instead of a request.

2.3
---

* Supported overriding max_age. This feature is only available for v2 tokens.

2.2
---

* Fixed crash on truncated v2 tokens.

2.1
---

* Added scoped tokens. This feature is only available for v2 tokens.

2.0
---

* Introduced a faster and shorter token format (v2). The previous format (v1)
  is still supported. See :ref:`Tokens security`.
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
