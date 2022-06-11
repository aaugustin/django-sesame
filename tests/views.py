from django.http import HttpResponse
from django.template import engines


def show_user(request, *args, **kwargs):
    content = (
        engines["django"]
        .from_string(
            "{% if user.is_authenticated %}{{ user }}"
            "{% elif user.is_anonymous %}anonymous"
            "{% else %}no user"
            "{% endif %}"
        )
        .render(request=request)
    )
    return HttpResponse(content, content_type="text/plain")
