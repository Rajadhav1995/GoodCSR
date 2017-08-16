# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budgetmanagement', '0003_auto_20170813_1402'),
        ('taskmanagement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='super_category',
            field=models.ForeignKey(blank=True, to='budgetmanagement.SuperCategory', null=True),
        ),
        migrations.AddField(
            model_name='historicalactivity',
            name='super_category',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='budgetmanagement.SuperCategory', null=True),
        ),
        migrations.AddField(
            model_name='historicaltask',
            name='activity',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='taskmanagement.Activity', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='object_id',
            field=models.IntegerField(verbose_name='object ID'),
        ),
        migrations.AlterField(
            model_name='historicalactivity',
            name='object_id',
            field=models.IntegerField(verbose_name='object ID'),
        ),
        migrations.RemoveField(
            model_name='task',
            name='activity',
        ),
        migrations.AddField(
            model_name='task',
            name='activity',
            field=models.ForeignKey(default=0, to='taskmanagement.Activity'),
            preserve_default=False,
        ),
    ]
