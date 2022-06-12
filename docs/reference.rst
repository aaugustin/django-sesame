API reference
=============

Settings
--------

.. admonition:: Changing settings invalidates all existing tokens.
    :class: warning

    The format of tokens depends on settings. As a consequence, changing any
    setting invalidates all existing tokens. There is a limited exception for
    :data:`SESAME_MAX_AGE`.

    For this reason, you should configure settings carefully before you start
    generating tokens.

.. data:: SESAME_TOKEN_NAME
    :value: "sesame"

    Name of the query string parameter containing the authentication token.

.. data:: SESAME_MAX_AGE
    :value: None

    Lifetime of authentications tokens, as a :class:`datetime.timedelta` or a
    number of seconds.

    When :data:`SESAME_MAX_AGE` is :obj:`None`, tokens always have an unlimited
    lifetime.

    When :data:`SESAME_MAX_AGE` is not :obj:`None`, you can adjust the desired
    lifetime in any API that accepts a ``max_age`` argument.

    .. admonition:: Changing :data:`SESAME_MAX_AGE` doesn't always invalidate
            tokens.
        :class: tip

        Changing the value of :data:`SESAME_MAX_AGE` doesn't invalidate tokens
        as long as it isn't :obj:`None`.

        The new value applies to all tokens, even those that were generated
        before the change.

        Only switching it between :obj:`None` and another value invalidates all
        tokens.

.. data:: SESAME_ONE_TIME
    :value: False

    Set :data:`SESAME_ONE_TIME` to :obj:`True` to invalidate tokens when they're
    used.

    Specifically, updating the user's last login date invalidates tokens.

.. data:: SESAME_INVALIDATE_ON_PASSWORD_CHANGE
    :value: True

    By default, tokens are invalidated when a user changes their password.

    Set :data:`SESAME_INVALIDATE_ON_PASSWORD_CHANGE` to :obj:`False` to prevent
    this.

.. data:: SESAME_PACKER
    :value: None

    Dotted path to a built-in or custom packer. See :ref:`Custom primary keys`.

.. data:: SESAME_TOKENS
    :value: ["sesame.tokens_v2", "sesame.tokens_v1"]

    Supported token formats. New tokens are generated with the first format.
    Existing tokens are accepted in any format listed here.

    The default value means "generate tokens v2, accept tokens v2 and v1". No
    other versions exist at this time.

.. data:: SESAME_KEY
    :value: ""

    Change the value of this setting if you need to invalidate all tokens.

    This setting only applies to tokens v2. See :ref:`Tokens security`.

.. data:: SESAME_SIGNATURE_SIZE
    :value: 10

    Size of the signature in bytes.

    This setting only applies to tokens v2. See :ref:`Tokens security`.

.. data:: SESAME_SALT
    :value: "sesame"

    Change the value of this setting if you need to invalidate all tokens.

    This setting only applies to tokens v1. See :ref:`Tokens security`.

.. SESAME_DIGEST was never documented and tokens v1 are superseded by tokens v2.

.. SESAME_ITERATIONS was never documented and tokens v1 are superseded by tokens v2.

Token generation
----------------

django-sesame provides three utility functions for generating tokens,
according to the context.

.. autofunction:: sesame.utils.get_query_string

.. autofunction:: sesame.utils.get_parameters

.. autofunction:: sesame.utils.get_token

Token validation
----------------

django-sesame provides high-level APIs to authenticate a user or to log
them in permanently.

.. autoclass:: sesame.middleware.AuthenticationMiddleware

.. autoclass:: sesame.views.LoginView

.. autodecorator:: sesame.decorators.authenticate

django-sesame also provides a low-level utility function for validating tokens.

.. autofunction:: sesame.utils.get_user

Token customization
-------------------

.. autoclass:: sesame.packers.BasePacker
    :members:

    See :ref:`Custom primary keys`.

Authentication backend
----------------------

django-sesame requires configuring a compatible authentication backend in
:setting:`AUTHENTICATION_BACKENDS`.

.. autoclass:: sesame.backends.ModelBackend

.. autoclass:: sesame.backends.SesameBackendMixin

    .. automethod:: authenticate
