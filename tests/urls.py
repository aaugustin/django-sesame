from django.urls import re_path

from .views import show_user

urlpatterns = [
    re_path("", show_user),  # catchall pattern
]
