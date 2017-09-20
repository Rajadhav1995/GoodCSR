# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-20 11:29
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields
import projectmanagement.models


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanagement', '0009_auto_20170913_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='attrs',
            field=jsonfield.fields.JSONField(default=projectmanagement.models.my_default),
        ),
    ]
