# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-08-08 11:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetmanagement', '0027_auto_20190808_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supercategory',
            name='menu_list',
            field=models.ManyToManyField(blank=True, default=[14, 18], null=True, related_name='super_menu', to='userprofile.Menus'),
        ),
    ]
