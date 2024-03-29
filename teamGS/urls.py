"""teamGS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, re_path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from core import views as core_views
from soccer import views as soccer_views

from nba import views as nba_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.index, name="index"),
    path('login/', core_views.user_login, name="login"),
    path('logout/', core_views.user_logout, name="logout"),
    path('join/', core_views.join, name="join"),
    path('about/', core_views.about, name="about"),
    path('soccer/team-page/', soccer_views.team_page, name="soccer-team-page"),
    path('soccer/', soccer_views.index, name="soccer-index"),
    path('soccer/team-not-found/', soccer_views.team_not_found),
    path('soccer/upcoming-matches/<int:team_id>/',
         soccer_views.upcoming_matches),
    path('soccer/team-page/toggle-like/',
         soccer_views.toggle_team_like, name="soccer-toggle-like"),
    path('nba/', nba_views.index, name="nba-index"),
    path('nba/team-page/', nba_views.team_page, name="nba-team-page"),
    path('soccer/team-not-found/', nba_views.team_not_found),
    path('nba/team-page/toggle-like/',
         nba_views.toggle_team_like, name="nba-toggle-like"),
    path('soccer/chat/<str:room_name>/',
         soccer_views.room, name="soccer-chat-room"),
    path('nba/chat/<str:room_name>/', nba_views.room, name="nba-chat-room"),
    path('soccer/team-page/<str:team_name>/',
         soccer_views.team_page, name="soccer-team-page"),
    path('nba/team-page/<str:team_name>/',
         nba_views.team_page, name="nba-team-page"),
    path('get-liked-teams/', core_views.getLikedTeams),
    path('nba_team_autocomplete/', nba_views.team_autocomplete.as_view(),
         name='nba_team_autocomplete'),
    path('soccer_team_autocomplete/', soccer_views.team_autocomplete.as_view(),
         name="soccer_team_autocomplete"),
    path('update-nba-live-games/', nba_views.update_live_games),
]
