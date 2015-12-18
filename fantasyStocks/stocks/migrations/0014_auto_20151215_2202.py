# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0013_auto_20151215_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 16, 3, 42, 52, 925311, tzinfo=utc)),
        ),
    ]
