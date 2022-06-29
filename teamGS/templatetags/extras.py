from django import template
from django.template.defaultfilters import stringfilter
from soccer.views import getLikedSoccerTeams
from nba.views import getLikedNBATeams
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
def get_liked_soccer_teams(username):
    user = User.objects.get(username=username)
    liked_soccer_teams = getLikedSoccerTeams(user)
    return liked_soccer_teams

@register.simple_tag
def get_liked_nba_teams(username):
    user = User.objects.get(username=username)
    liked_nba_teams = getLikedNBATeams(user)
    return liked_nba_teams

@register.simple_tag
def get_username(user):
    logged_in =  (user != "")
    if logged_in == True:
        return user
    else:
        return "anonymous"


