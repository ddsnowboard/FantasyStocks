# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0011_auto_20151212_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='last_price',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 16, 0, 54, 49, 954815, tzinfo=utc)),
        ),
    ]
