from __future__ import unicode_literals

from django.conf.urls import url
from django.http import HttpResponse
from django.template import engines

template = engines['django'].from_string(
    '{% if user.is_authenticated %}{{ user }}'
    '{% elif user.is_anonymous %}anonymous'
    '{% else %}no user'
    '{% endif %}'
)


def show_user(request):
    content = template.render(request=request)
    return HttpResponse(content, content_type='text/plain')


urlpatterns = [
    url(r'^', show_user),
]
