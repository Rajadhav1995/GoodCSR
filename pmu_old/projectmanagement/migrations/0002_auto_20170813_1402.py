# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projectmanagement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalProjectUserRoleRelationship',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('role', models.CharField(max_length=300, null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical project user role relationship',
            },
        ),
        migrations.CreateModel(
            name='KeyParameter',
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
            name='keyParameterValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=300, null=True, blank=True)),
                ('parameter_value', models.CharField(max_length=300, null=True, blank=True)),
                ('object_id', models.IntegerField(verbose_name='object ID')),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_keyparametervalue', verbose_name='content type', to='contenttypes.ContentType')),
                ('keyparameter', models.ForeignKey(to='projectmanagement.KeyParameter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MasterCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('code', models.CharField(max_length=100, null=True, blank=True)),
                ('slug', models.SlugField(max_length=255, null=True, verbose_name=b'Slug', blank=True)),
                ('parent', models.ForeignKey(blank=True, to='projectmanagement.MasterCategory', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectUserRoleRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(max_length=300, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user_reference_id', models.IntegerField(default=0)),
                ('email', models.CharField(max_length=500, null=True, blank=True)),
                ('orgnaization', models.CharField(max_length=800, null=True, blank=True)),
                ('organization_type', models.IntegerField(default=0)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='historicaluserroleproject',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicaluserroleproject',
            name='project',
        ),
        migrations.RemoveField(
            model_name='historicaluserroleproject',
            name='role',
        ),
        migrations.RemoveField(
            model_name='userroleproject',
            name='project',
        ),
        migrations.RemoveField(
            model_name='userroleproject',
            name='role',
        ),
        migrations.RemoveField(
            model_name='userroleproject',
            name='user',
        ),
        migrations.AlterField(
            model_name='historicalproject',
            name='created_by',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projectmanagement.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproject',
            name='object_id',
            field=models.IntegerField(verbose_name='object ID'),
        ),
        migrations.AlterField(
            model_name='program',
            name='created_by',
            field=models.ForeignKey(related_name='program_created_user', blank=True, to='projectmanagement.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='created_by',
            field=models.ForeignKey(related_name='created_user', blank=True, to='projectmanagement.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='object_id',
            field=models.IntegerField(verbose_name='object ID'),
        ),
        migrations.DeleteModel(
            name='HistoricalUserRoleProject',
        ),
        migrations.DeleteModel(
            name='Role',
        ),
        migrations.DeleteModel(
            name='UserRoleProject',
        ),
        migrations.AddField(
            model_name='projectuserrolerelationship',
            name='project',
            field=models.ForeignKey(blank=True, to='projectmanagement.Project', null=True),
        ),
        migrations.AddField(
            model_name='projectuserrolerelationship',
            name='user',
            field=models.ForeignKey(blank=True, to='projectmanagement.UserProfile', null=True),
        ),
        migrations.AddField(
            model_name='keyparameter',
            name='parameter_type',
            field=models.ForeignKey(blank=True, to='projectmanagement.MasterCategory', null=True),
        ),
        migrations.AddField(
            model_name='historicalprojectuserrolerelationship',
            name='project',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projectmanagement.Project', null=True),
        ),
        migrations.AddField(
            model_name='historicalprojectuserrolerelationship',
            name='user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projectmanagement.UserProfile', null=True),
        ),
    ]
