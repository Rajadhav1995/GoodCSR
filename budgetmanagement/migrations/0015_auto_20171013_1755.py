# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-13 12:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetmanagement', '0014_auto_20171013_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='slug',
            field=models.SlugField(blank=True, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='question',
            name='qtype',
            field=models.CharField(choices=[(b'T', b'Text Input'), (b'S', b'Select One Choice'), (b'R', b'Radio List'), (b'C', b'Checkbox List'), (b'D', b'Date'), (b'M', b'Master'), (b'F', b'File Field'), (b'Q', b'API Question'), (b'DD', b'Drop Down'), (b'OT', b'Other type'), (b'MC', b'Multi-Checkbox'), (b'ck', b'CKeditor'), (b'APT', b'Auto Populate Text'), (b'API', b'Auto Populate Image')], max_length=10, verbose_name='question type'),
        ),
    ]
