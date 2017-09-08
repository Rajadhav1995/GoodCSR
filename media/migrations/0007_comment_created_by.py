# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-08 09:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanagement', '0008_auto_20170908_0628'),
        ('media', '0006_auto_20170830_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_created_user', to='projectmanagement.UserProfile'),
        ),
    ]
