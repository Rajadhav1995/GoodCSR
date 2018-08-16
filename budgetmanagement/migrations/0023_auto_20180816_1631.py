# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-16 11:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetmanagement', '0022_auto_20180816_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='block',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='budget',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='budgetperiodunit',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='historicalbudget',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='historicalbudgetperiodunit',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='historicalprojectbudgetperiodconf',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='historicalsupercategory',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='historicaltranche',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='projectbudgetperiodconf',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='quarterreportsection',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='question',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='removequestion',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='reportmilestoneactivity',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='reportparameter',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='supercategory',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='survey',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
        migrations.AlterField(
            model_name='tranche',
            name='active',
            field=models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2),
        ),
    ]
