# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_auto_20151129_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floor',
            name='floorPlayer',
            field=models.ForeignKey(to='stocks.Player', null=True, related_name='FloorPlayer'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 29, 22, 14, 42, 85846, tzinfo=utc)),
        ),
    ]
