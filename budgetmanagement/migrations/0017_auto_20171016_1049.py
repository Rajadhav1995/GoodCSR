# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-16 05:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('budgetmanagement', '0016_block_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content_type_set_for_answer', to='contenttypes.ContentType', verbose_name='content type'),
        ),
        migrations.AddField(
            model_name='answer',
            name='object_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='object ID'),
        ),
    ]
