API reference
=============

Generating URLs
---------------

django-sesame provides functions to generate authenticated URLs in the
``sesame.utils`` module.

Load a user from the database:

.. code:: pycon

    >>> from django.contrib.auth import get_user_model
    >>> User = get_user_model()
    >>> user = User.objects.first()

Now you can create a query string that you can append to any URL to enable
one-click login:

.. code:: pycon

    >>> from sesame.utils import get_query_string
    >>> get_query_string(user)
    '?sesame=zxST9d0XT9xgfYLvoa9e2myN'

You can also obtain a ``dict`` of URL parameters rather than ready-to-use
query string:

.. code:: pycon

    >>> from sesame.utils import get_parameters
    >>> get_parameters(user)
    {'sesame': 'zxST9d0XT9xgfYLvoa9e2myN'}

Then you can add other URL parameters to this ``dict`` before serializing it
to a query string.

Finally, here's how to get only the token:

.. code:: pycon

    >>> from sesame.utils import get_token
    >>> get_token(user)
    'zxST9d0XT9xgfYLvoa9e2myN'

Share the resulting URLs with your users though an adequately confidential
channel for your use case.

By default, the URL parameter is named ``sesame``. You can change this with
the ``SESAME_TOKEN_NAME`` setting. Make sure that it doesn't conflict with
other query string parameters used by your application.

*Changed in 2.0:* the URL parameter used to be named ``url_auth_token``.
