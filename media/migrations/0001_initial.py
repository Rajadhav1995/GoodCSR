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
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('attachment_file', models.FileField(null=True, upload_to=b'static/%Y/%m/%d', blank=True)),
                ('name', models.CharField(max_length=300, null=True, verbose_name=b'Description', blank=True)),
                ('description', models.CharField(max_length=600, null=True, verbose_name=b'Description', blank=True)),
                ('attachment_type', models.IntegerField(blank=True, null=True, verbose_name=b'ATTACHMENT_TYPE', choices=[(1, b'Image'), (2, b'Documents')])),
                ('document_type', models.IntegerField(blank=True, null=True, verbose_name=b'DOCUMENT_TYPE', choices=[(1, b'Excel'), (2, b'PDF'), (3, b'PPT'), (4, b'Word Document')])),
                ('date', models.DateTimeField(null=True, blank=True)),
                ('object_id', models.IntegerField(null=True, verbose_name='object ID', blank=True)),
                ('URL', models.URLField(verbose_name=b'Link url', blank=True)),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_attachment', verbose_name='content type', blank=True, to='contenttypes.ContentType', null=True)),
                ('parent', models.ForeignKey(blank=True, to='media.Attachment', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.PositiveIntegerField(default=2, choices=[(0, b'Inactive'), (2, b'Active')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('area', models.CharField(max_length=200, null=True, blank=True)),
                ('ward_no', models.CharField(max_length=50, null=True, blank=True)),
                ('pin_code', models.CharField(max_length=50, null=True, blank=True)),
                ('program_type', models.IntegerField(default=0, choices=[(0, b'Urban'), (1, b'Semi-urban'), (2, b'Rural')])),
                ('object_id', models.IntegerField(null=True, verbose_name='object ID', blank=True)),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_projectlocation', verbose_name='content type', blank=True, to='contenttypes.ContentType', null=True)),
                ('created_by', models.ForeignKey(blank=True, to='projectmanagement.UserProfile', null=True)),
                ('location', models.ForeignKey(blank=True, to='projectmanagement.Boundary', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
