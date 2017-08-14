# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budgetmanagement', '0002_auto_20170811_0837'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicaltranche',
            old_name='disbursed_amount',
            new_name='recommended_amount',
        ),
        migrations.RenameField(
            model_name='tranche',
            old_name='disbursed_amount',
            new_name='recommended_amount',
        ),
        migrations.RemoveField(
            model_name='historicaltranche',
            name='budget',
        ),
        migrations.RemoveField(
            model_name='tranche',
            name='budget',
        ),
        migrations.AddField(
            model_name='budgetperiodunit',
            name='rate',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='budgetperiodunit',
            name='remarks',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='budgetperiodunit',
            name='unit_type',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbudgetperiodunit',
            name='rate',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbudgetperiodunit',
            name='remarks',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalbudgetperiodunit',
            name='unit_type',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaltranche',
            name='disbursed_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaltranche',
            name='due_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaltranche',
            name='utilized_amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='projectbudgetperiodconf',
            name='end_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='projectbudgetperiodconf',
            name='start_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tranche',
            name='disbursed_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tranche',
            name='due_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tranche',
            name='utilized_amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='budgetperiodunit',
            name='created_by',
            field=models.ForeignKey(blank=True, to='projectmanagement.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='historicalbudgetperiodunit',
            name='created_by',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projectmanagement.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='historicaltranche',
            name='recommended_by',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projectmanagement.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='tranche',
            name='recommended_by',
            field=models.ForeignKey(blank=True, to='projectmanagement.UserProfile', null=True),
        ),
    ]
