Tokens lifecycle
----------------

By default, tokens don't expire but are tied to the password of the user.
Changing the password invalidates the token. When the authentication backend
uses salted passwords — that's been the default in Django for a long time —
the token is invalidated even if the new password is identical to the old one.

If you want tokens to expire after a given amount of time, set the
``SESAME_MAX_AGE`` setting to a duration in seconds or a
``datetime.timedelta``. Then each token will contain the time it was generated
at and django-sesame will check if it's still valid at each login attempt.

If you want tokens to be usable only once, set the ``SESAME_ONE_TIME`` setting
to ``True``. Then tokens are valid only if the last login date hasn't changed
since they were generated. Since logging in changes the last login date, such
tokens are usable at most once. If you're intending to send links by email, be
aware that some email providers scan links for security reasons, which
consumes single-use tokens prematurely. Tokens with a short expiry are more
reliable.

If you don't want tokens to be invalidated by password changes, set the
``SESAME_INVALIDATE_ON_PASSWORD_CHANGE`` setting to ``False``. **This is
discouraged because it becomes impossible to invalidate a single token.** Your
only option if a token is compromised is to invalidate all tokens at once. If
you're doing it anyway, you should set ``SESAME_MAX_AGE`` to a short value to
minimize risks. This option may be useful for generating tokens during a
sign up process, when you don't know if the token will be used before or after
initializing the password.

Finally, if the ``is_active`` attribute of a user is set to ``False``,
django-sesame rejects authentication tokens for this user.

Tokens must be verified with the same settings that were used for generating
them. Changing settings invalidates previously generated tokens. The only
exception to this rule is ``SESAME_MAX_AGE``: as long as it isn't ``None``,
you can change its value and the new value will apply even to previously
generated tokens.
