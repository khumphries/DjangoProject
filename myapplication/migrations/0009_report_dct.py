# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0008_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='dct',
            field=models.ForeignKey(null=True, to='myapplication.Dct'),
        ),
    ]
