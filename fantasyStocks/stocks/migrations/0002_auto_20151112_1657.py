# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floor',
            name='permissiveness',
            field=models.CharField(default='permissive', choices=[('open', 'Open'), ('closed', 'Closed'), ('permissive', 'Permissive')], max_length=15),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 12, 22, 37, 50, 147317, tzinfo=utc)),
        ),
    ]
