Per-view authentication
-----------------------

The configuration described in :ref:`Getting started` enables a middleware that
looks for a token in every request and, if there is a valid token, logs the
user in. It's as if they had submitted their username and password in a login
form. This provides compatibility with APIs like the ``login_required``
decorator and the ``LoginRequired`` mixin.

Sometimes this behavior is too blunt. For example, you may want to build a
Magic Link that gives access to a specific view but doesn't log the user in
permanently.

To achieve this, remove ``"sesame.middleware.AuthenticationMiddleware"`` from
the ``MIDDLEWARE`` setting and authenticate the user with django-sesame in a
view as follows:

.. code-block:: python

    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse

    from sesame.utils import get_user

    def hello(request):
        user = get_user(request)
        if user is None:
            raise PermissionDenied
        return HttpResponse("Hello {}!".format(user))

When ``get_user()`` returns ``None``, it means that the token was missing,
invalid, expired, or that the user account is inactive. Then you can show an
appropriate error message or redirect to a login form.

When ``SESAME_ONE_TIME`` is enabled, ``get_user()`` updates the user's last
login date in order to invalidate the token. When ``SESAME_ONE_TIME`` isn't
enabled, it doesn't, because making a database write for every call to
``get_user()`` could degrade performance. You can override this behavior with
the ``update_last_login`` keyword argument:

.. code-block:: python

    get_user(request, update_last_login=True)   # always update last_login
    get_user(request, update_last_login=False)  # never update last_login
