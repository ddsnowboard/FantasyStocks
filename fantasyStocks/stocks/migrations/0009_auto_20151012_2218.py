# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import stocks.models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0008_stock_change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='image',
            field=models.ImageField(upload_to=stocks.models.get_upload_location, blank=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 13, 2, 58, 18, 329533, tzinfo=utc)),
        ),
    ]
