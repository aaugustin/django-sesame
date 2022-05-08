Scoped tokens
-------------

If your application uses tokens for multiple purposes, you should prevent a
token created from one purpose from being reused for another purpose.

Add a ``scope`` to generate authenticated URLs valid only in that scope:

.. code:: pycon

    >>> from sesame.utils import get_query_string
    >>> get_query_string(user, scope="sharing")
    '?sesame=jISWHmrXr4zg8FHVZZuxhpHs'

Similar to ``get_query_string()``, ``get_parameters()`` and ``get_token()``
accept an optional ``scope`` argument. ``scope`` must be a string.

Then you can verify the token with the same scope:

.. code:: python

    from sesame.utils import get_user

    def share(request):
        user = get_user(request, scope="sharing")
        if user is None:
            raise PermissionDenied
        ...

If the scope doesn't match, the token is invalid and ``get_user()`` returns
``None``. ``get_user()`` is the only way to verify a scoped token.

The default scope is ``""``. ``"sesame.middleware.AuthenticationMiddleware"``
considers a token generated with a non-default scope to be invalid and doesn't
log the user in, even if the token is valid in that scope.
