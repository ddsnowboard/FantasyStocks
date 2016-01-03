# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0014_auto_20151215_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='floor',
            name='num_stocks',
            field=models.IntegerField(default=10),
        ),
        migrations.AddField(
            model_name='floor',
            name='public',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 22, 21, 36, 31, 447838, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='trade',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
