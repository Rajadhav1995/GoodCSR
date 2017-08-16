# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanagement', '0004_projectorganizationrelation'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectFunderRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('total_budget', models.IntegerField(default=0)),
                ('funder', models.ForeignKey(related_name='funder', to='projectmanagement.UserProfile')),
                ('implementation_partner', models.ForeignKey(related_name='implementation_partner', to='projectmanagement.UserProfile')),
                ('project', models.ForeignKey(blank=True, to='projectmanagement.Project', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='projectorganizationrelation',
            name='funder',
        ),
        migrations.RemoveField(
            model_name='projectorganizationrelation',
            name='implementation_partner',
        ),
        migrations.RemoveField(
            model_name='projectorganizationrelation',
            name='project',
        ),
        migrations.DeleteModel(
            name='ProjectOrganizationRelation',
        ),
    ]
