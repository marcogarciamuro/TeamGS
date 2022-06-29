from django.contrib import admin
from nba.models import Team, Article, Game

# Register your models here.
admin.site.register(Team)
admin.site.register(Article)
admin.site.register(Game)
