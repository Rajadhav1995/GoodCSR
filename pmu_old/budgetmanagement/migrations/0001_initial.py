# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('heading', models.CharField(max_length=200, null=True, blank=True)),
                ('expenses_type', models.IntegerField(blank=True, null=True, choices=[(1, b'Programmatic'), (2, b'Non-programmatic')])),
                ('order', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BudgetPeriodUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('subheading', models.CharField(max_length=200, null=True, blank=True)),
                ('unit', models.CharField(max_length=200, null=True, blank=True)),
                ('planned_unit_cost', models.CharField(max_length=200, null=True, blank=True)),
                ('utilized_unit_cost', models.CharField(max_length=200, null=True, blank=True)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalBudgetPeriodUnit',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('subheading', models.CharField(max_length=200, null=True, blank=True)),
                ('unit', models.CharField(max_length=200, null=True, blank=True)),
                ('planned_unit_cost', models.CharField(max_length=200, null=True, blank=True)),
                ('utilized_unit_cost', models.CharField(max_length=200, null=True, blank=True)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('order', models.IntegerField(default=0)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical budget period unit',
            },
        ),
        migrations.CreateModel(
            name='HistoricalSuperCategory',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('slug', models.SlugField(verbose_name='Slug', blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical super category',
            },
        ),
        migrations.CreateModel(
            name='HistoricalTranche',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('planned_amount', models.IntegerField(default=0)),
                ('actual_disbursed_amount', models.IntegerField(default=0)),
                ('disbursed_amount', models.IntegerField(default=0)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical tranche',
            },
        ),
        migrations.CreateModel(
            name='ProjectBudgetPeriodConf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=300, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SuperCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('slug', models.SlugField(verbose_name='Slug', blank=True)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tranche',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('planned_amount', models.IntegerField(default=0)),
                ('actual_disbursed_amount', models.IntegerField(default=0)),
                ('disbursed_amount', models.IntegerField(default=0)),
                ('budget', models.ForeignKey(blank=True, to='budgetmanagement.BudgetCategory', null=True)),
                ('budget_period', models.ForeignKey(blank=True, to='budgetmanagement.ProjectBudgetPeriodConf', null=True)),
                ('recommended_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
