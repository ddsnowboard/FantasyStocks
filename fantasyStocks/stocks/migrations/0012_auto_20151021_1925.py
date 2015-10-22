# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime
from django.conf import settings
import stocks.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocks', '0011_auto_20151013_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='floor',
            name='owner',
            field=models.ForeignKey(default=2, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stock',
            name='image',
            field=models.ImageField(upload_to=stocks.models.get_upload_location, default='/home/ddsnowboard/Programming/FantasyStocks/fantasyStocks/res/default', blank=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 22, 0, 3, 11, 20707, tzinfo=utc)),
        ),
    ]
