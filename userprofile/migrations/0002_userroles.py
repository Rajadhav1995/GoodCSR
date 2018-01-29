# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-29 08:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanagement', '0011_auto_20171113_1254'),
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRoles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=254)),
                ('role_type', models.ManyToManyField(blank=True, to='userprofile.RoleTypes')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_role_relation', to='projectmanagement.UserProfile')),
            ],
            options={
                'verbose_name_plural': 'User Roles',
            },
        ),
    ]
