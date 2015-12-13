# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0010_auto_20151209_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 12, 15, 59, 0, 360369, tzinfo=utc)),
        ),
    ]
