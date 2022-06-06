Authentication outside views
----------------------------

You may want to authenticate users outside of a Django view, where there's no
``request`` object available. To support this use case, ``get_user()`` also
accepts a token directly:

.. code-block:: python

    sesame = get_sesame(...)  # getting a token from somewhere else
    user = get_user(sesame)
