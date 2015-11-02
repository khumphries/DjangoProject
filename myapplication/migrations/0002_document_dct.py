# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='dct',
            field=models.ForeignKey(null=True, to='myapplication.Dct'),
        ),
    ]
