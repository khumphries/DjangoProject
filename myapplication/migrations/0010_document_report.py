# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0009_report_dct'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='report',
            field=models.ForeignKey(to='myapplication.Report', null=True),
        ),
    ]
