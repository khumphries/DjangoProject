# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0006_message_encrypt'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='sentDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 21, 20, 35, 28, 925102, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='subject',
            field=models.CharField(default='subject', max_length=50),
        ),
    ]
