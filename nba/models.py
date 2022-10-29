from django.db import models
from django.contrib.auth.models import User
from datetime import date


class NewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    # formatted_name = models.CharField(max_length=100, blank=True, default=None, null=True)
    nickname = models.CharField(max_length=100, blank=True)
    teamID = models.IntegerField()
    conference = models.CharField(max_length=4)
    rank = models.PositiveSmallIntegerField(blank=True, null=True)
    wins = models.PositiveSmallIntegerField(blank=True, null=True)
    losses = models.PositiveSmallIntegerField(blank=True, null=True)
    win_pct = models.DecimalField(max_digits=4, decimal_places=3, null=True)
    logo = models.ImageField(max_length=255)
    liked_by = models.ManyToManyField(
        User, related_name='%(class)s_liked_nba_teams', default=None, blank=True)
    last_updated = models.DateField(default=date.today)
    objects = models.Manager()
    new_manager = NewManager()


class Game(models.Model):
    game_id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=10)
    quarter = models.PositiveSmallIntegerField(null=True, blank=True)
    home_team = models.ForeignKey(
        Team, related_name="home_game", on_delete=models.CASCADE)
    away_team = models.ForeignKey(
        Team, related_name="away_game",  on_delete=models.CASCADE)
    home_team_points = models.IntegerField(blank=True, null=True)
    away_team_points = models.IntegerField(blank=True, null=True)
    date = models.DateField(blank=True)

    class Meta:
        get_latest_by = ['date']


class Article(models.Model):
    team = models.ForeignKey(Team, default=None,
                             blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, primary_key=True)
    author = models.CharField(max_length=100, blank=True)
    thumbnail = models.CharField(max_length=200)
    description = models.CharField(max_length=300)
    url = models.CharField(max_length=100)
    retrieval_date = models.DateField(default=date.today, blank=True)
    objects = models.Manager()
    new_manager = NewManager()

    class Meta:
        get_latest_by = ['retrieval_date']
