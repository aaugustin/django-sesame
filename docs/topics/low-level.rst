Low-level authentication
------------------------

``get_user()`` is a thin wrapper around the low-level ``authenticate()``
function from ``django.contrib.auth``. It's also possible to verify an
authentication token directly with  ``authenticate()``. To do so, the
``sesame.backends.ModelBackend`` authentication backend expects an
``sesame`` argument:

.. code-block:: python

    from django.contrib.auth import authenticate

    user = authenticate(sesame=...)

*Changed in 2.0:* the argument used to be named ``url_auth_token``.

If you decide to use ``authenticate()`` instead of ``get_user()``, you must
update ``user.last_login`` to invalidate one-time tokens. Indeed, in
``django.contrib.auth``, ``authenticate()`` is a low-level function. The
caller, usually the higher-level ``login()`` function, is responsible for
updating ``user.last_login``.
