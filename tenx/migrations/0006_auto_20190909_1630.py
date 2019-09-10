# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-09-09 23:30
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenx', '0005_auto_20190801_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaltenxlane',
            name='gsc_sublibrary_names',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=10, null=True), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='tenxlane',
            name='gsc_sublibrary_names',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=10, null=True), blank=True, null=True, size=None),
        ),
    ]