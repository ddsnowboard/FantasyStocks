# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0009_auto_20151208_1826'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockSuggestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('floor', models.ForeignKey(to='stocks.Floor')),
                ('requesting_player', models.ForeignKey(to='stocks.Player')),
            ],
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 9, 18, 52, 46, 523559, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='stocksuggestion',
            name='stock',
            field=models.ForeignKey(to='stocks.Stock'),
        ),
    ]
