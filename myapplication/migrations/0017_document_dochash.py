# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0016_auto_20151129_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='dochash',
            field=models.BinaryField(null=True),
        ),
    ]
