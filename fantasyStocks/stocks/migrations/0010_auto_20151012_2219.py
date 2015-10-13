# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0009_auto_20151012_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='company_name',
            field=models.CharField(max_length=50, default='', blank=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 13, 2, 59, 39, 496450, tzinfo=utc)),
        ),
    ]
