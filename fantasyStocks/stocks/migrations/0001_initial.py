# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stocks.models
from django.utils.timezone import utc
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=35)),
                ('permissiveness', models.CharField(default='open', choices=[('open', 'Open'), ('closed', 'Closed'), ('permissive', 'Permissive')], max_length=15)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('points', models.IntegerField(default=0)),
                ('floor', models.ForeignKey(to='stocks.Floor')),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('company_name', models.CharField(default='', blank=True, max_length=50)),
                ('symbol', models.CharField(max_length=4)),
                ('last_updated', models.DateTimeField(default=datetime.datetime(2015, 11, 12, 22, 31, 11, 976931, tzinfo=utc))),
                ('image', models.ImageField(default='/images/default', blank=True, upload_to=stocks.models.get_upload_location)),
                ('price', models.DecimalField(default=0, max_digits=6, decimal_places=2)),
                ('change', models.DecimalField(default=0, max_digits=6, decimal_places=2)),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='stocks',
            field=models.ManyToManyField(to='stocks.Stock'),
        ),
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='floor',
            name='stocks',
            field=models.ManyToManyField(to='stocks.Stock'),
        ),
    ]
