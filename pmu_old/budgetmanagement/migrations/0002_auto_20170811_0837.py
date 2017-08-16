# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanagement', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('budgetmanagement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supercategory',
            name='project',
            field=models.ForeignKey(blank=True, to='projectmanagement.Project', null=True),
        ),
        migrations.AddField(
            model_name='projectbudgetperiodconf',
            name='project',
            field=models.ForeignKey(to='projectmanagement.Project'),
        ),
        migrations.AddField(
            model_name='historicaltranche',
            name='budget',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='budgetmanagement.BudgetCategory', null=True),
        ),
        migrations.AddField(
            model_name='historicaltranche',
            name='budget_period',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='budgetmanagement.ProjectBudgetPeriodConf', null=True),
        ),
        migrations.AddField(
            model_name='historicaltranche',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicaltranche',
            name='recommended_by',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalsupercategory',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalsupercategory',
            name='project',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projectmanagement.Project', null=True),
        ),
        migrations.AddField(
            model_name='historicalbudgetperiodunit',
            name='budget_heading',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='budgetmanagement.BudgetCategory', null=True),
        ),
        migrations.AddField(
            model_name='historicalbudgetperiodunit',
            name='budget_period',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='budgetmanagement.ProjectBudgetPeriodConf', null=True),
        ),
        migrations.AddField(
            model_name='historicalbudgetperiodunit',
            name='created_by',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalbudgetperiodunit',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='budgetperiodunit',
            name='budget_heading',
            field=models.ForeignKey(blank=True, to='budgetmanagement.BudgetCategory', null=True),
        ),
        migrations.AddField(
            model_name='budgetperiodunit',
            name='budget_period',
            field=models.ForeignKey(blank=True, to='budgetmanagement.ProjectBudgetPeriodConf', null=True),
        ),
        migrations.AddField(
            model_name='budgetperiodunit',
            name='created_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='budgetcategory',
            name='parent',
            field=models.ForeignKey(blank=True, to='budgetmanagement.BudgetCategory', null=True),
        ),
        migrations.AddField(
            model_name='budgetcategory',
            name='super_category',
            field=models.ForeignKey(to='budgetmanagement.SuperCategory'),
        ),
    ]
