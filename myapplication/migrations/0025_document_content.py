# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0024_remove_document_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='content',
            field=models.BinaryField(null=True),
        ),
    ]
