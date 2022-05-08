Stateless authentication
------------------------

Theoretically, django-sesame can provide stateless authenticated navigation
without ``django.contrib.sessions``, provided all internal links include the
authentication token. That increases the security concerns and it's unclear
that it meets any practical use case.

In a scenario where ``django.contrib.sessions.middleware.SessionMiddleware``
and ``django.contrib.auth.middleware.AuthenticationMiddleware`` aren't
enabled, ``sesame.middleware.AuthenticationMiddleware`` still sets
``request.user`` to the currently logged-in user or ``AnonymousUser()``.
