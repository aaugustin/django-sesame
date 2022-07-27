User guide
==========

Generate tokens
---------------

A django-sesame token authenticates a user when they access your app. All you
need to generate a token is a user instance.

For example, let's load a user from the database:

.. code-block:: pycon

    >>> from django.contrib.auth import get_user_model
    >>> User = get_user_model()
    >>> user = User.objects.first()

Let's define a target URL:

.. code-block:: pycon

    >>> LOGIN_URL = "https://example.com/sesame/login/"

You can add a django-sesame token to this URL with
:func:`sesame.utils.get_query_string`:

.. code-block:: pycon

    >>> from sesame.utils import get_query_string
    >>> LOGIN_URL + get_query_string(user)
    'https://example.com/sesame/login/?sesame=zxST9d0XT9xgfYLvoa9e2myN'

Now you can share this URL with the user via any channel providing appropriate
confidentiality. This part is highly dependent on your use case. django-sesame
leaves it up to you.

.. admonition:: By default, the query string parameter is called ``sesame``.
    :class: tip

    You can change it with the :data:`SESAME_TOKEN_NAME` setting. Avoid
    conflicts with other parameters in your application.

    .. versionchanged:: 2.0

        the URL parameter used to be named ``url_auth_token``.

At a lower level, you can obtain a :class:`dict` of URL parameters with
:func:`sesame.utils.get_parameters`:

.. code-block:: pycon

    >>> from sesame.utils import get_parameters
    >>> get_parameters(user)
    {'sesame': 'zxST9d0XT9xgfYLvoa9e2myN'}

This makes it more convenient to add more query string parameters to the URL:

.. code-block:: pycon

    >>> from sesame.utils import get_parameters
    >>> from urllib.parse import urlencode
    >>> query_params = get_parameters(user)
    >>> query_params["next"] = "/welcome/"
    >>> LOGIN_URL + "?" + urlencode(query_params)
    'https://example.com/sesame/login/?sesame=zxST9d0XT9xgfYLvoa9e2myN&next=%2Fwelcome%2F'

Finally, you can get the token itself with :func:`sesame.utils.get_token`:

.. code-block:: pycon

    >>> from sesame.utils import get_token
    >>> get_token(user)
    'zxST9d0XT9xgfYLvoa9e2myN'

Indeed, you can use django-sesame tokens in other contexts than URLs served by a
Django app, for example to `authenticate WebSocket connections`__.

__ https://websockets.readthedocs.io/en/stable/howto/django.html#generate-tokens

.. versionadded:: 2.0

    :func:`~sesame.utils.get_token` was added.

Authenticate tokens
-------------------

django-sesame provides four mechanisms for authenticating tokens, addressing
different use cases and supporting different levels of customization.

Site-wide
.........

:class:`sesame.middleware.AuthenticationMiddleware` performs authentication
across your application.

With this middleware, you can add a token to any URL and log the user in as if
they had gone through a login form. This enables one-click access to views
protected by the :func:`~django.contrib.auth.decorators.login_required`
decorator or the :class:`~django.contrib.auth.mixins.LoginRequiredMixin`
class-based view mixin.

To enable the middleware, add ``"sesame.middleware.AuthenticationMiddleware"``
to the :setting:`MIDDLEWARE` setting. Place it just after Django's
:class:`~django.contrib.auth.middleware.AuthenticationMiddleware`:

.. code-block:: python

    MIDDLEWARE = [
        ...,
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "sesame.middleware.AuthenticationMiddleware",
        ...,
    ]

After a successful login, the token is removed from the URL with an HTTP 302
Redirect.

.. admonition:: This functionality requires additional setup for Safari.
    :class: warning

    :class:`~sesame.middleware.AuthenticationMiddleware` requires the optional
    ``ua`` extra to prevent :ref:`issues with Safari <Safari issues>`:

    .. code-block:: console

        $ pip install 'django-sesame[ua]'

This method works well when security concerns are limited and you want the
convenience of adding a django-sesame token to any URL e.g.
``https://example.com/welcome/?sesame=<...>``.

Login view
..........

.. versionadded:: 3.0

:class:`sesame.views.LoginView` provides the same functionality as Django's
built-in :class:`~django.contrib.auth.views.LoginView`, except it looks for
a django-sesame token in the URL instead of asking for credentials.

Configure the view in your URLconf:

.. code-block:: python

    from django.urls import path
    from sesame.views import LoginView

    urlpatterns = [
        ...,
        path("sesame/login/", LoginView.as_view(), name="sesame-login"),
        ...,
    ]

URLs become longer e.g.
``https://example.com/sesame/login/?sesame=<...>&next=%2Fwelcome%2F``. On the
positive side, enabling authentication at only one URL yields security benefits:
it's easier to add throttling, to monitor traffic, etc.

View decorator
..............

.. versionadded:: 3.0

Sometimes the behavior of :class:`~sesame.middleware.AuthenticationMiddleware`
and :class:`~sesame.views.LoginView` is too blunt. Maybe you want to authorize
access to a specific view without logging the user in. Or maybe you want to
:ref:`restrict tokens to specific scopes <Scoped tokens>`.

Decorate a view with :func:`sesame.decorators.authenticate` to look for a token
and set ``request.user``.

:func:`~sesame.decorators.authenticate` may be applied to a view directly:

.. code-block:: python

    from django.http import HttpResponse
    from sesame.decorators import authenticate

    @authenticate
    def hello(request):
        return HttpResponse(f"Hello {request.user}!")

Or it may be applied with arguments:

.. code-block:: python

    @authenticate(override=False)
    def hello(request):
        return HttpResponse(f"Hello {request.user}!")

:func:`~sesame.decorators.authenticate` can be configured to provide several behaviors:

* When no valid token is found, it may return a HTTP 403 Forbidden error or,
  when ``required=False``, set ``request.user`` to an
  :class:`~django.contrib.auth.models.AnonymousUser`.
* When a valid token is found, it may set ``request.user`` to the corresponding
  user or, when ``permanent=True``, also log the user in permanently.
* When a user is already logged in and a valid token is found, it may override
  ``request.user`` or, when ``override=False``, ignore the token.

Custom view logic
.................

You can call the low-level :func:`sesame.utils.get_user` function to
authenticate a user directly:

.. code-block:: python

    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse

    from sesame.utils import get_user

    def hello(request):
        user = get_user(request)
        if user is None:
            raise PermissionDenied
        return HttpResponse(f"Hello {user}!")

:func:`~sesame.utils.get_user` returns :obj:`None` when no valid token is found.
Then you can show an appropriate error message or redirect to a login mechanism.

Outside a view
..............

You may want to authenticate users outside of a Django view, where there's no
:class:`~django.http.HttpRequest` object available. To support this use case,
:func:`~sesame.utils.get_user` also accepts a token directly.

.. code-block:: python

    from sesame.utils import get_user

    user = get_user(token)

In other words, you may use :func:`~sesame.utils.get_user` as the inverse of
:func:`~sesame.utils.get_token`.

.. versionchanged:: 2.4

    the ability to pass a token to :func:`~sesame.utils.get_user` was added.

Low-level
.........

The low-level :func:`~django.contrib.auth.authenticate` function provided by
:mod:`django.contrib.auth` can verify a token directly:

.. code-block:: python

    from django.contrib.auth import authenticate

    user = authenticate(sesame=token)

.. versionchanged:: 2.0

    the argument used to be named ``url_auth_token``.

Then, you can log the user in with :func:`~django.contrib.auth.login`.

While this is technically possible, it is best to stick with
:func:`~sesame.utils.get_user` because :func:`~django.contrib.auth.authenticate`
doesn't invalidate single-use tokens.

Tokens expiration
-----------------

When you configure django-sesame, you must decide whether tokens will expire or
will remain valid forever. You cannot mix expiring and non-expiring tokens
within the same project.

In most cases, expiring tokens are a better choice:

* You get better security properties, especially in case a token leaks.
* You can customize the lifetime of tokens to support different use cases.
* You can emulate non-expiring tokens by configuring a very long lifetime.

Set the :data:`SESAME_MAX_AGE` setting to enable expiring tokens and to
configure their lifetime. It may be expressed as a :class:`~datetime.timedelta`
or a duration in seconds.

.. versionchanged:: 2.0

    support for :class:`~datetime.timedelta` was added.

If you have several use cases requiring different lifetimes, you can override
:data:`SESAME_MAX_AGE` when you authenticate a token.

:class:`~sesame.views.LoginView`, :func:`~sesame.decorators.authenticate`, and
:func:`~sesame.utils.get_user` support a ``max_age`` argument:

.. code-block:: python

    from sesame.utils import get_user

    user = get_user(token, max_age=180)  # 180 seconds = 3 minutes

.. versionchanged:: 2.3

    the possibility to override ``max_age`` was added.

You cannot override :data:`SESAME_MAX_AGE` when you generate a token because
tokens store only the time when they were created, not their expected lifetime.

Non-expiring are acceptable for simple cases where tokens should remain valid
forever and where security concerns are low.

Set :data:`SESAME_MAX_AGE` to :obj:`None`, its default value, to generate
non-expiring tokens. They don't store the time when they were created. As a
consequence, if you need to switch to expiring tokens later, you will have to
change :data:`SESAME_MAX_AGE`, which will invalidate all existing tokens.

Single-use tokens
-----------------

If you set the :data:`SESAME_ONE_TIME` setting to :obj:`True`, tokens will be
usable only once.

.. admonition:: Authenticating with a single-use token always updates the user's
        last login date.
    :class: warning

    This is how django-sesame :ref:`invalidates single-use tokens <Single-use>`
    after they're used.

Like expiration, this is a global setting for the project. Changing it
invalidates all existing tokens.

Tokens with a short lifetime are often a better choice than single-use tokens
because they don't require the user to obtain a new token in many circumstances
where the token gets invalidated before serving its purpose.

For example, when doing :ref:`login by email <Login by email>`, the client could
timeout while fetching the response. In that case, the user may click the link
again, but the token was invalidated by their first attempt. They would get a
better experience if the link still worked.

Scoped tokens
-------------

.. versionadded:: 2.1

If your application uses tokens for multiple purposes, you should prevent a
token created for one purpose from being reused for another purpose.

You achieve this by assigning a scope to tokens. You must provide the same scope
when you generate a token and when you authenticate it. Else, it's invalid.

For example, if you're generating a token for giving access to the report with
ID 66, you can set the token's scope to ``"report:66"``.

.. admonition:: The default scope (``""``) behaves exactly like any other scope.
    :class: tip

    Tokens generated with the default scope are only valid in the default scope.
    Tokens generated with another scope aren't valid in the default scope.

    You should reserve the default scope for logging users in. Any other use
    case warrants a dedicated scope.

:func:`~sesame.utils.get_query_string`, :func:`~sesame.utils.get_parameters`,
and :func:`~sesame.utils.get_token` accept an optional ``scope`` argument to
generate scoped tokens:

.. code-block:: pycon

    >>> from sesame.utils import get_query_string
    >>> report_id = 66
    >>> get_token(user, scope=f"report:{report_id}")
    'jISWHmrXr4zg8FHVZZuxhpHs'

:class:`~sesame.views.LoginView`, :func:`~sesame.decorators.authenticate`, and
:func:`~sesame.utils.get_user` accept the same ``scope`` argument to
authenticate scoped tokens:

.. code-block:: python

    from sesame.utils import get_user

    def share_report(request, report_id):
        user = get_user(request, scope=f"report:{report_id}")
        if user is None:
            raise PermissionDenied
        ...

This view can be implemented more concisely, albeit more magically, as follows:

.. code-block:: python

    from sesame.decorators import authenticate

    @authenticate(scope="report:{report_id}")
    def share_report(request, report_id):
        ...

.. admonition:: :class:`~sesame.middleware.AuthenticationMiddleware` doesn't support scopes.
    :class: warning

    It only accepts tokens generated with the default scope.
