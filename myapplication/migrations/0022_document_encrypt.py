# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0021_auto_20151205_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='encrypt',
            field=models.BooleanField(default=False),
        ),
    ]
