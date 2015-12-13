# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0005_auto_20151129_1634'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Trade',
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 29, 22, 40, 0, 153653, tzinfo=utc)),
        ),
    ]
