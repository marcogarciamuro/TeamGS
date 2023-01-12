from django.contrib import admin

# Register your models here.
from soccer.models import Team, League, Article, Player, TeamArticle, LeagueArticle
admin.site.register(Team)
admin.site.register(League)
admin.site.register(Article)
admin.site.register(Player)
admin.site.register(TeamArticle)
admin.site.register(LeagueArticle)
