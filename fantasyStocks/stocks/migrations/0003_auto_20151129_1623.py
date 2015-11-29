# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_auto_20151112_1657'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='floor',
            name='floorPlayer',
            field=models.ForeignKey(null=True, related_name='FloorPlayer', to='stocks.Player'),
        ),
        migrations.AlterField(
            model_name='player',
            name='stocks',
            field=models.ManyToManyField(blank=True, to='stocks.Stock'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 29, 22, 3, 56, 767946, tzinfo=utc)),
        ),
    ]
