# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-07-23 21:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20190719_1543'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalsample',
            name='pipeline_tag',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='pipeline_tag',
        ),
    ]
