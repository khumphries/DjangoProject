# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0004_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='display',
            field=models.BooleanField(default=True),
        ),
    ]
