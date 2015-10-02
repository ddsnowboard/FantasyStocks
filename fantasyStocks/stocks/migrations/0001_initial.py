# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stocks.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('symbol', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('lastUpdated', models.DateField()),
                ('image', models.ImageField(upload_to=stocks.models.get_upload_location)),
            ],
        ),
    ]
