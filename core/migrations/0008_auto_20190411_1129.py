# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-11 18:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20190410_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenxpool',
            name='libraries',
            field=models.ManyToManyField(to='core.TenxLibrary'),
        ),
    ]