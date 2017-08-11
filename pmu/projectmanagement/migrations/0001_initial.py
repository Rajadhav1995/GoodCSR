# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Boundary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('boundary_level', models.IntegerField(default=0)),
                ('slug', models.SlugField(max_length=255, null=True, verbose_name=b'Slug', blank=True)),
                ('parent', models.ForeignKey(blank=True, to='projectmanagement.Boundary', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalProject',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('request_status', models.IntegerField(default=0, choices=[(0, b''), (1, b'Requested'), (2, b'Request more information'), (3, b'Reject'), (4, b'Approved'), (5, b'ShortList'), (6, b'Decision Pending')])),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('total_budget', models.IntegerField(default=0)),
                ('budget_type', models.IntegerField(default=2, choices=[(1, b'Yearly'), (2, b'Quarterly'), (3, b'Half Yearly')])),
                ('project_status', models.IntegerField(default=0, choices=[(0, b''), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')])),
                ('duration', models.IntegerField(default=0)),
                ('summary', ckeditor.fields.RichTextField(null=True, blank=True)),
                ('tagline', ckeditor.fields.RichTextField(null=True, blank=True)),
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
                'verbose_name': 'historical project',
            },
        ),
        migrations.CreateModel(
            name='HistoricalUserRoleProject',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical user role project',
            },
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('description', models.TextField(null=True, verbose_name=b'About Project', blank=True)),
                ('created_by', models.ForeignKey(related_name='program_created_user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('request_status', models.IntegerField(default=0, choices=[(0, b''), (1, b'Requested'), (2, b'Request more information'), (3, b'Reject'), (4, b'Approved'), (5, b'ShortList'), (6, b'Decision Pending')])),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('total_budget', models.IntegerField(default=0)),
                ('budget_type', models.IntegerField(default=2, choices=[(1, b'Yearly'), (2, b'Quarterly'), (3, b'Half Yearly')])),
                ('project_status', models.IntegerField(default=0, choices=[(0, b''), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')])),
                ('duration', models.IntegerField(default=0)),
                ('summary', ckeditor.fields.RichTextField(null=True, blank=True)),
                ('tagline', ckeditor.fields.RichTextField(null=True, blank=True)),
                ('slug', models.SlugField(verbose_name='Slug', blank=True)),
                ('object_id', models.TextField(verbose_name='object ID')),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_project', verbose_name='content type', to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='created_user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('location', models.ManyToManyField(related_name='project_location', to='projectmanagement.Boundary', blank=True)),
                ('program', models.ForeignKey(blank=True, to='projectmanagement.Program', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserRoleProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(blank=True, to='projectmanagement.Project', null=True)),
                ('role', models.ForeignKey(blank=True, to='projectmanagement.Role', null=True)),
                ('user', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='historicaluserroleproject',
            name='project',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projectmanagement.Project', null=True),
        ),
        migrations.AddField(
            model_name='historicaluserroleproject',
            name='role',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projectmanagement.Role', null=True),
        ),
        migrations.AddField(
            model_name='historicalproject',
            name='program',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projectmanagement.Program', null=True),
        ),
    ]
