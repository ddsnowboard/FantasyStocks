# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0003_stock_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(),
        ),
    ]
