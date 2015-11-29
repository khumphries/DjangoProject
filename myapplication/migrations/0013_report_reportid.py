# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0012_report_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='reportID',
            field=models.UUIDField(editable=False, default=uuid.uuid4),
        ),
    ]
