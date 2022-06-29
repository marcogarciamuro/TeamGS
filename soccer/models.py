from django.db import models
from django.contrib.auth.models import User
from datetime import date
# Create your models here.

class NewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

class Team(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    # city = models.CharField(max_length=100)
    teamID = models.IntegerField()
    leagueID = models.IntegerField()
    logo = models.ImageField()
    liked_by = models.ManyToManyField(
        User, related_name='%(class)s_liked_soccer_teams', default=None, blank=True)
    objects = models.Manager()
    new_manager = NewManager()

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

class League(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    leagueID = models.IntegerField()
    logo = models.ImageField()
    # team = models.ForeignKey(Team, on_delete=models.CASCADE)

