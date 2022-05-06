from django.urls import path, re_path

from sesame.views import LoginView

from .views import show_user

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("login/no_redirect/", LoginView.as_view(next_page=None)),
    re_path("", show_user),  # catchall pattern
]
