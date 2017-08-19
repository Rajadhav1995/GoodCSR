# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-17 05:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('attachment_file', models.FileField(blank=True, null=True, upload_to=b'static/%Y/%m/%d')),
                ('name', models.CharField(blank=True, max_length=300, null=True, verbose_name=b'Description')),
                ('description', models.CharField(blank=True, max_length=600, null=True, verbose_name=b'Description')),
                ('attachment_type', models.IntegerField(blank=True, choices=[(1, b'Image'), (2, b'Documents')], null=True, verbose_name=b'ATTACHMENT_TYPE')),
                ('document_type', models.IntegerField(blank=True, choices=[(1, b'Excel'), (2, b'PDF'), (3, b'PPT'), (4, b'Word Document')], null=True, verbose_name=b'DOCUMENT_TYPE')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('object_id', models.IntegerField(blank=True, null=True, verbose_name='object ID')),
                ('URL', models.URLField(blank=True, verbose_name=b'Link url')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.PositiveIntegerField(choices=[(0, b'Inactive'), (2, b'Active')], default=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('area', models.CharField(blank=True, max_length=200, null=True)),
                ('ward_no', models.CharField(blank=True, max_length=50, null=True)),
                ('pin_code', models.CharField(blank=True, max_length=50, null=True)),
                ('program_type', models.IntegerField(choices=[(0, b'Urban'), (1, b'Semi-urban'), (2, b'Rural')], default=0)),
                ('object_id', models.IntegerField(blank=True, null=True, verbose_name='object ID')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content_type_set_for_projectlocation', to='contenttypes.ContentType', verbose_name='content type')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
