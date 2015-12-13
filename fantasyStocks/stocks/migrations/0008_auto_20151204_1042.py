# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0007_auto_20151129_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 12, 4, 10, 42, 1, 287615)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 4, 16, 21, 42, 177846, tzinfo=utc)),
        ),
    ]
