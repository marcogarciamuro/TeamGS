# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.


class NewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class League(models.Model):
    league_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(blank=True)


class Team(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    teamID = models.IntegerField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    logo = models.ImageField()
    liked_by = models.ManyToManyField(
        User, related_name='%(class)s_liked_soccer_teams', default=None, blank=True)
    objects = models.Manager()
    new_manager = NewManager()

    @classmethod
    def create(cls, name, teamID, league, logo, liked_by):
        team = cls(name=name, teamID=teamID, league=league,
                   logo=logo, likedBy=liked_by)
        return team


class Article(models.Model):
    title = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100, blank=True)
    thumbnail = models.CharField(max_length=200)
    description = models.CharField(max_length=300)
    url = models.CharField(max_length=100)
    retrieval_date = models.DateTimeField(default=now, blank=True)
    objects = models.Manager()
    new_manager = NewManager()

    class Meta:
        get_latest_by = ['retrieval_date']


class TeamArticle(Article):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class LeagueArticle(Article):
    league = models.ForeignKey(League, on_delete=models.CASCADE)


class Player(models.Model):
    player_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField(null=True)
    team = models.ForeignKey(Team, default=None, on_delete=models.CASCADE)
    height_feet = models.PositiveSmallIntegerField(null=True)
    height_inches = models.PositiveSmallIntegerField(null=True)
    weight = models.PositiveSmallIntegerField(null=True)
    photo = models.ImageField()
    nationality = models.CharField(max_length=100, null=True)
    jersey_number = models.PositiveSmallIntegerField(null=True)
    position = models.CharField(null=True, max_length=1)
