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
from django.contrib.staticfiles.views import serve

def return_static(request, path, insecure=True, **kwargs):
    return serve(request, path, insecure, **kwargs)


# Solution to serving static files using daphne and not using manage.py runserver
# https://pythonmana.com/2022/01/202201110420226037.html

urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', return_static, name='static'),
    path('admin/', admin.site.urls),
    path('', core_views.index),
    path('login/', core_views.user_login),
    path('logout/', core_views.user_logout),
    path('join/', core_views.join),
    path('about/', core_views.about),
    path('soccer/team-page/', soccer_views.team_page),
    re_path('soccer/team-page/(?P<team_name>[a-zA-Z]*-?[a-zA-Z]*)/$', soccer_views.team_page),
    re_path('soccer/team-page/(?P<team_name>[Pp]aris-[Ss]aint-[Gg]ermain)/$', soccer_views.team_page),
    path('soccer/', soccer_views.index),
    path('soccer/team-not-found/', soccer_views.team_not_found),
    path('soccer/upcoming-matches/<int:id>/', soccer_views.upcoming_matches),
    path('soccer/team-page/toggle-like/<str:team_name>/', soccer_views.toggleLike),
    path('nba/', nba_views.index),
    path('nba/team-page/', nba_views.team_page),
    path('soccer/team-not-found/', nba_views.team_not_found),
    re_path('nba/team-page/(?P<team_name>[a-zA-Z]*[-?[a-zA-Z]*]*)/$', nba_views.team_page),
    path('nba/team-page/toggle-like/<str:team_name>/', nba_views.toggleLike),
    path('soccer/liked', soccer_views.liked_list),
    path('soccer/chat/<str:room_name>/', soccer_views.room),
    path('nba/chat/<str:room_name>/', nba_views.room),
    path('soccer/team-page/<str:team_name>/', soccer_views.team_page)
]
