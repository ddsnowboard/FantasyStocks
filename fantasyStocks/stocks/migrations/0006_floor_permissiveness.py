# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0005_floor_player'),
    ]

    operations = [
        migrations.AddField(
            model_name='floor',
            name='permissiveness',
            field=models.CharField(max_length=15, default='permissive', choices=[('open', 'Open'), ('closed', 'Closed'), ('permissive', 'Permissive')]),
        ),
    ]
