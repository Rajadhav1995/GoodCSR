# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('projectmanagement', '0002_auto_20170813_1402'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrimaryWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('types', models.IntegerField(blank=True, null=True, choices=[(0, b'Primary Activities'), (1, b'Scope of work')])),
                ('name', models.TextField(null=True, blank=True)),
                ('number', models.IntegerField(default=0)),
                ('activity_duration', models.IntegerField(default=0)),
                ('object_id', models.IntegerField(null=True, verbose_name='object ID', blank=True)),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_primarywork', verbose_name='content type', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='historicalproject',
            name='tagline',
        ),
        migrations.RemoveField(
            model_name='project',
            name='tagline',
        ),
        migrations.AddField(
            model_name='historicalproject',
            name='no_of_beneficiaries',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='keyparameter',
            name='project',
            field=models.ForeignKey(blank=True, to='projectmanagement.Project', null=True),
        ),
        migrations.AddField(
            model_name='keyparametervalue',
            name='date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='cause_area',
            field=models.ManyToManyField(related_name='area_category', to='projectmanagement.MasterCategory', blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='no_of_beneficiaries',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='target_beneficiaries',
            field=models.ManyToManyField(related_name='target_beneficiaries', to='projectmanagement.MasterCategory', blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_admin_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='owner',
            field=models.BooleanField(default=False),
        ),
    ]
