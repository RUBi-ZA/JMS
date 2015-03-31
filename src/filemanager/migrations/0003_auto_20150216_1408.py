# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filemanager', '0002_auto_20150118_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='filemanagersettings',
            name='Key',
            field=models.CharField(max_length=64, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filemanagersettings',
            name='Salt',
            field=models.CharField(max_length=8, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filemanagersettings',
            name='ServerPass',
            field=models.CharField(max_length=1024, null=True, blank=True),
            preserve_default=True,
        ),
    ]
