# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapplication', '0020_auto_20151205_0431'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('Q1', models.CharField(max_length=30)),
                ('Q2', models.CharField(max_length=30)),
                ('Q3', models.CharField(max_length=30)),
                ('securityowner', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='securityowner')),
            ],
        ),
        migrations.RemoveField(
            model_name='securityquestions',
            name='securityowner',
        ),
        migrations.DeleteModel(
            name='SecurityQuestions',
        ),
    ]
