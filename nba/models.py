from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.


class NewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class Conference(models.Model):
    region = models.CharField(max_length=4, primary_key=True)


class Team(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    # formatted_name = models.CharField(max_length=100, blank=True, default=None, null=True)
    nickname = models.CharField(max_length=100, blank=True)
    teamID = models.IntegerField()
    conference = models.ForeignKey(
        Conference, db_column='conference', related_name="team_conference", on_delete=models.CASCADE, default=None, blank=True)
    rank = models.PositiveSmallIntegerField(blank=True, null=True)
    wins = models.PositiveSmallIntegerField(blank=True, null=True)
    losses = models.PositiveSmallIntegerField(blank=True, null=True)
    win_pct = models.DecimalField(max_digits=4, decimal_places=3, null=True)
    logo = models.ImageField(max_length=255)
    liked_by = models.ManyToManyField(
        User, related_name='%(class)s_liked_nba_teams', default=None, blank=True)
    last_updated = models.DateTimeField()
    created_on = models.DateTimeField()
    objects = models.Manager()
    new_manager = NewManager()

    def __unicode__(self):
        return self.name


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
    date = models.DateTimeField()

    class Meta:
        get_latest_by = ['date']


class Article(models.Model):
    title = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100, blank=True)
    thumbnail = models.CharField(max_length=200)
    description = models.CharField(max_length=300)
    url = models.CharField(max_length=150)
    retrieval_date = models.DateTimeField(default=now, blank=True)
    objects = models.Manager()
    new_manager = NewManager()

    class Meta:
        get_latest_by = ['retrieval_date']


class TeamArticle(Article):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class NBAArticle(Article):
    association = models.CharField(max_length=3, default="NBA")


class Player(models.Model):
    player_id = models.PositiveIntegerField(primary_key=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField(null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    height_feet = models.PositiveSmallIntegerField(null=True)
    height_inches = models.PositiveSmallIntegerField(null=True)
    weight = models.PositiveSmallIntegerField(null=True)
    jersey_number = models.PositiveSmallIntegerField(null=True)
    position = models.CharField(null=True, max_length=10)
