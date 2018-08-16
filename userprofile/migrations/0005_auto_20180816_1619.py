# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-16 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_merge_20180222_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalprojectuserrolerelationship',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], db_index=True, default=2),
        ),
        migrations.AlterField(
            model_name='historicalroleconfig',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], db_index=True, default=2),
        ),
        migrations.AlterField(
            model_name='menus',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], db_index=True, default=2),
        ),
        migrations.AlterField(
            model_name='projectuserrolerelationship',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], db_index=True, default=2),
        ),
        migrations.AlterField(
            model_name='roleconfig',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], db_index=True, default=2),
        ),
        migrations.AlterField(
            model_name='roletypes',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], db_index=True, default=2),
        ),
        migrations.AlterField(
            model_name='userroles',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], db_index=True, default=2),
        ),
    ]
