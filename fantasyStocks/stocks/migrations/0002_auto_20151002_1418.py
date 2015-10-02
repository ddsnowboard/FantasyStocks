# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stock',
            old_name='lastUpdated',
            new_name='last_updated',
        ),
        migrations.AddField(
            model_name='stock',
            name='company_name',
            field=models.CharField(default='', max_length=50),
        ),
    ]
