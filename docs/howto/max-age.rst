Override expiration
-------------------

If you have several use cases inside the same application and they require
different expiry durations, you can override ``SESAME_MAX_AGE``:

.. code-block:: python

    from sesame.utils import get_user

    def recover(request):
        user = get_user(request, max_age=120)
        if user is None:
            raise PermissionDenied
        ...

This doesn't work when ``SESAME_MAX_AGE`` is ``None`` — because tokens don't
contain a timestamp in that case. In other words, changing the expiry duration
is supported, but switching between expiring and non-expiring tokens isn't.
