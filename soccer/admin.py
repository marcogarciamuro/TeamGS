from django.contrib import admin

# Register your models here.
from soccer.models import Team, League, Article
admin.site.register(Team)
admin.site.register(League)
admin.site.register(Article)

