# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0013_report_reportid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='reportID',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
