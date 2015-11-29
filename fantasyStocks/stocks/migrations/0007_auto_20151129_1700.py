# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0006_auto_20151129_1700'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('floor', models.ForeignKey(to='stocks.Floor')),
                ('recipient', models.ForeignKey(to='stocks.Player')),
            ],
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 29, 22, 40, 12, 865966, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='trade',
            name='recipientStocks',
            field=models.ManyToManyField(to='stocks.Stock', related_name='receivingPlayerStocks'),
        ),
        migrations.AddField(
            model_name='trade',
            name='sender',
            field=models.ForeignKey(to='stocks.Player', related_name='sendingPlayer'),
        ),
        migrations.AddField(
            model_name='trade',
            name='senderStocks',
            field=models.ManyToManyField(to='stocks.Stock'),
        ),
    ]
