from django.urls import path, re_path

from sesame.decorators import authenticate
from sesame.views import LoginView

from .views import show_user

urlpatterns = [
    # For test_decorators.TestAuthenticate
    path("authenticate/", authenticate(show_user)),
    path("authenticate/not_required/", authenticate(required=False)(show_user)),
    path("authenticate/permanent/", authenticate(permanent=True)(show_user)),
    path("authenticate/no_override/", authenticate(override=False)(show_user)),
    path("authenticate/scope/", authenticate(scope="scope")(show_user)),
    re_path(
        r"authenticate/scope/arg/([a-z]+)/",
        authenticate(scope="arg:{}")(show_user),
    ),
    re_path(
        r"authenticate/scope/kwarg/(?P<kwarg>[a-z]+)/",
        authenticate(scope="kwarg:{kwarg}")(show_user),
    ),
    # For test_views.TestLoginView
    path("login/", LoginView.as_view()),
    path("login/no_redirect/", LoginView.as_view(next_page=None)),
    # For test_middleware.TestMiddleware
    re_path("", show_user),  # catchall pattern
]
