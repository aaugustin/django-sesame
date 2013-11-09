from __future__ import unicode_literals

from django.conf.urls import patterns
from django.http import HttpResponse
from django.template import RequestContext, Template


template = Template(
    '{% if user.is_authenticated %}{{ user }}'
    '{% elif user.is_anonymous %}anonymous'
    '{% else %}no user'
    '{% endif %}'
)


def show_user(request):
    context = RequestContext(request)
    return HttpResponse(template.render(context), content_type='text/plain')


urlpatterns = patterns('', (r'^', show_user))
