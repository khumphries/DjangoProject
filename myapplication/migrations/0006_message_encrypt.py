# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0005_message_display'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='encrypt',
            field=models.BooleanField(default=False),
        ),
    ]
