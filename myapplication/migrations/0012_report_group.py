# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0011_remove_document_dct'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report_Group',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('group', models.CharField(max_length=80)),
                ('report', models.ForeignKey(to='myapplication.Report')),
            ],
        ),
    ]
