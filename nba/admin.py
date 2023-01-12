from django.contrib import admin
from nba.models import Team, Article, Game, Conference, Player, TeamArticle, NBAArticle

# Register your models here.
admin.site.register(Team)
admin.site.register(Article)
admin.site.register(TeamArticle)
admin.site.register(Game)
admin.site.register(Conference)
admin.site.register(Player)
admin.site.register(NBAArticle)
