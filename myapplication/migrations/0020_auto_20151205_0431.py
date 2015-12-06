# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapplication', '0019_securityquestions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='securityquestions',
            old_name='owner',
            new_name='securityowner',
        ),
    ]
