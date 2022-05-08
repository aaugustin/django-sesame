Getting started
===============

1. Install django-sesame:

   .. code:: shell-session

    $ pip install django-sesame[ua]

   The ``ua`` extra is optional. See :ref:`Safari issues` for details.

2. Add ``"sesame.backends.ModelBackend"`` to the
   |AUTHENTICATION_BACKENDS setting|__. Extending the default value, this looks
   like:

   .. |AUTHENTICATION_BACKENDS setting| replace:: ``AUTHENTICATION_BACKENDS`` setting
   __ https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-AUTHENTICATION_BACKENDS

   .. code:: python

    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
        "sesame.backends.ModelBackend",
    ]

3. Add ``"sesame.middleware.AuthenticationMiddleware"`` to the ``MIDDLEWARE``
   setting, just after Django’s ``AuthenticationMiddleware``:

   .. code:: python

    MIDDLEWARE = [
        ...,
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "sesame.middleware.AuthenticationMiddleware",
        ...,
    ]
