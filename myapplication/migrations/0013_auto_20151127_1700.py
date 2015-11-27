# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import myapplication.models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0012_report_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='name',
            field=models.CharField(default='dummy_report', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dct',
            name='stName',
            field=models.CharField(validators=[myapplication.models.validate_dct_stName], max_length=50),
        ),
        migrations.AlterField(
            model_name='report',
            name='shortDescription',
            field=models.CharField(validators=[myapplication.models.validate_report_name], max_length=50),
        ),
    ]
