# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import myapplication.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('stName', models.CharField(max_length=80, validators=[myapplication.models.validate_dct_stName])),
                ('dctParent', models.ForeignKey(to='myapplication.Dct', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('dct', models.ForeignKey(to='myapplication.Dct')),
            ],
        ),
    ]
