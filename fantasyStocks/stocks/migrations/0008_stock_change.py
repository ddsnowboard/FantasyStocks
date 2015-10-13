# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0007_floor_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='change',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=6),
        ),
    ]
