# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-13 07:24
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanagement', '0010_userprofile_attrs'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproject',
            name='program_aim',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='program_aim',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
