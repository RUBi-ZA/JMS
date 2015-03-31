# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filemanager', '0003_auto_20150216_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filemanagersettings',
            name='Key',
        ),
        migrations.RemoveField(
            model_name='filemanagersettings',
            name='Salt',
        ),
    ]
