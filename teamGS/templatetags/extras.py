from django import template
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import User
import os

register = template.Library()


@register.simple_tag
def get_env_var(key):
    return os.environ.get(key)


@register.filter
@stringfilter
def replace(string):
    return string.replace("-", " ")


@register.filter
@stringfilter
def removeSpaces(string):
    return string.replace(" ", "-")


# https://docs.djangoproject.com/en/4.0/howto/custom-template-tags/

@register.simple_tag
def get_username(user):
    logged_in = (user != "")
    if logged_in == True:
        return user
    else:
        return "anonymous"
