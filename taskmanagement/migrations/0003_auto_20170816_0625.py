# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanagement', '0002_auto_20170814_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b' '), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')]),
        ),
        migrations.AlterField(
            model_name='historicalactivity',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b' '), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')]),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b' '), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b' '), (1, b'Open'), (2, b'Close'), (3, b'Ongoing')]),
        ),
    ]
