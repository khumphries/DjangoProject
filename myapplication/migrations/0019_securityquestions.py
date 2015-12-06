# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapplication', '0018_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityQuestions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('Q1', models.CharField(max_length=30)),
                ('Q2', models.CharField(max_length=30)),
                ('Q3', models.CharField(max_length=30)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='owner')),
            ],
        ),
    ]
