# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_auto_20151002_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='price',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=2),
        ),
    ]
