# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0006_floor_permissiveness'),
    ]

    operations = [
        migrations.AddField(
            model_name='floor',
            name='name',
            field=models.CharField(max_length=15, default='Untitled'),
            preserve_default=False,
        ),
    ]
