# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=600, null=True, blank=True)),
                ('activity_type', models.IntegerField(default=0, choices=[(1, b'Core'), (2, b'Non-core')])),
                ('status', models.IntegerField(default=0, choices=[(0, b''), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')])),
                ('description', models.TextField(null=True, blank=True)),
                ('slug', models.SlugField(verbose_name='Slug', blank=True)),
                ('object_id', models.TextField(verbose_name='object ID')),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_activity', verbose_name='content type', to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='activity_created_user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalActivity',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('name', models.CharField(max_length=600, null=True, blank=True)),
                ('activity_type', models.IntegerField(default=0, choices=[(1, b'Core'), (2, b'Non-core')])),
                ('status', models.IntegerField(default=0, choices=[(0, b''), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')])),
                ('description', models.TextField(null=True, blank=True)),
                ('slug', models.SlugField(verbose_name='Slug', blank=True)),
                ('object_id', models.TextField(verbose_name='object ID')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('content_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='contenttypes.ContentType', null=True)),
                ('created_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical activity',
            },
        ),
        migrations.CreateModel(
            name='HistoricalMilestone',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('name', models.CharField(max_length=300, null=True, blank=True)),
                ('overdue', models.DateTimeField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical milestone',
            },
        ),
        migrations.CreateModel(
            name='HistoricalTask',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('name', models.CharField(max_length=600, null=True, blank=True)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('slug', models.SlugField(verbose_name='Slug', blank=True)),
                ('actual_start_date', models.DateTimeField(null=True, blank=True)),
                ('actual_end_date', models.DateTimeField(null=True, blank=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b''), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('created_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical task',
            },
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=300, null=True, blank=True)),
                ('overdue', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=600, null=True, blank=True)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('slug', models.SlugField(verbose_name='Slug', blank=True)),
                ('actual_start_date', models.DateTimeField(null=True, blank=True)),
                ('actual_end_date', models.DateTimeField(null=True, blank=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b''), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')])),
                ('activity', models.ManyToManyField(to='taskmanagement.Activity', blank=True)),
                ('created_by', models.ForeignKey(related_name='task_assigned_user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='milestone',
            name='task',
            field=models.ManyToManyField(to='taskmanagement.Task', blank=True),
        ),
    ]
