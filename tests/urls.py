from django.urls import path, re_path

from sesame.decorators import authenticate
from sesame.views import LoginView

from .views import show_user

urlpatterns = [
    path("authenticate/", authenticate(show_user)),
    path("authenticate/not_required/", authenticate(required=False)(show_user)),
    path("authenticate/permanent/", authenticate(permanent=True)(show_user)),
    path("authenticate/no_override/", authenticate(override=False)(show_user)),
    path("login/", LoginView.as_view()),
    path("login/no_redirect/", LoginView.as_view(next_page=None)),
    re_path("", show_user),  # catchall pattern
]
