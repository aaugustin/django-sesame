django-sesame
=============

.. toctree::
    :hidden:

    tutorial
    howto/index
    reference
    topics/index
    contributing
    changelog

Getting started
---------------

Install django-sesame:

.. code-block:: console

    $ pip install django-sesame

Open your project settings and add ``"sesame.backends.ModelBackend"`` to the
|AUTHENTICATION_BACKENDS setting|__. Extending the default value, this looks
like:

.. |AUTHENTICATION_BACKENDS setting| replace:: ``AUTHENTICATION_BACKENDS`` setting
__ https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-AUTHENTICATION_BACKENDS

.. code-block:: python

    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
        "sesame.backends.ModelBackend",
    ]

Now, your project can authenticate users based on django-sesame tokens.
