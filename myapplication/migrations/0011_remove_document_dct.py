# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0010_document_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='dct',
        ),
    ]
