from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User
from soccer.models import Team

# Create your models here.
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     liked_teams = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE) 

#     def __str__(self):
#         return self.user.username