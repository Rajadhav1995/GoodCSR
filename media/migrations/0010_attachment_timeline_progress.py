# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-04 06:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0009_contactpersoninformation'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='timeline_progress',
            field=models.BooleanField(default=False),
        ),
    ]
