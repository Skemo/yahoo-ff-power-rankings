import datetime

from decimal import Decimal
from django.db import models
from django.utils import timezone


class Teams(models.Model):
    team_key = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    league_year = models.IntegerField(default=datetime.datetime.now().year)
    wins = models.IntegerField(default=0)
    manager = models.CharField(max_length=100)
    logo = models.CharField(max_length=256)
    current_roster_rank = models.IntegerField(default=0)


class ScoringLog(models.Model):
    team = models.ForeignKey(Teams, related_name='teams')
    created = models.DateTimeField(default=timezone.now)
    week = models.IntegerField()
    points_scored = models.DecimalField(max_digits=5, decimal_places=2)


class PowerRankingsData(models.Model):
    team = models.ForeignKey(Teams, related_name='rank_teams')
    week = models.IntegerField()
    win_rank = models.IntegerField(default=0)
    ovw_rank = models.IntegerField(default=0)
    con_rank = models.IntegerField(default=0)
    avg_rank = models.IntegerField(default=0)
    ros_rank = models.IntegerField(default=0)
    pow_rank = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal(0.00))