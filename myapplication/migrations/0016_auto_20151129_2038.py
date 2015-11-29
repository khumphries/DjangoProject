# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import myapplication.models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0015_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='name',
            field=models.CharField(validators=[myapplication.models.validate_report_name], max_length=50, default='dummy_report'),
        ),
        migrations.AlterField(
            model_name='report',
            name='shortDescription',
            field=models.CharField(max_length=50),
        ),
    ]
