# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-06 10:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanagement', '0006_auto_20170826_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='mastercategory',
            name='category_type',
            field=models.TextField(blank=True, choices=[(b'DBC', b'Direct to Beneficiary Cost'), (b'IC', b'Indirect Cost'), (b'AC', b'Admin Cost'), (b'O', b'Others')], null=True),
        ),
    ]
