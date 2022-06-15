django-sesame
=============

.. toctree::
    :hidden:

    tutorial
    howto/index
    reference
    topics/index
    faq
    contributing
    changelog

Getting started
---------------

Install django-sesame:

.. code-block:: console

    $ pip install django-sesame

Open your project settings and add ``"sesame.backends.ModelBackend"`` to the
:setting:`AUTHENTICATION_BACKENDS` setting. Extending the default value, this
looks like:

.. code-block:: python

    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
        "sesame.backends.ModelBackend",
    ]

Now, your project can authenticate users based on django-sesame tokens.
