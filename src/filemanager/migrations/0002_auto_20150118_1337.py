# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filemanager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='filemanagersettings',
            name='FontSize',
            field=models.IntegerField(default=11),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='filemanagersettings',
            name='HomeDirectory',
            field=models.TextField(default=b'/'),
            preserve_default=True,
        ),
    ]
