# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-05 17:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0005_auto_20161005_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='powerrankingsdata',
            name='pow_rank',
            field=models.IntegerField(default=0),
        ),
    ]