# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-12 17:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20190411_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsample',
            name='sample_type',
            field=models.CharField(blank=True, choices=[('P', 'Patient'), ('C', 'Cell Line'), ('X', 'Xenograft'), ('Or', 'Organoid'), ('O', 'Other')], max_length=50, null=True, verbose_name='Sample type'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='sample_type',
            field=models.CharField(blank=True, choices=[('P', 'Patient'), ('C', 'Cell Line'), ('X', 'Xenograft'), ('Or', 'Organoid'), ('O', 'Other')], max_length=50, null=True, verbose_name='Sample type'),
        ),
        migrations.AddField(
            model_name='historicaltenxlibrary',
            name='experimental_condition',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Experimental condition'),
        ),
        migrations.AddField(
            model_name='tenxlibrary',
            name='experimental_condition',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Experimental condition'),
        ),
        migrations.AlterField(
            model_name='historicaltenxlibrary',
            name='description',
            field=models.TextField(blank=True, max_length=1024, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='tenxlibrary',
            name='description',
            field=models.TextField(blank=True, max_length=1024, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='historicaltenxlibrary',
            name='google_sheet',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Google Sheet Link'),
        ),
        migrations.AlterField(
            model_name='tenxlibrary',
            name='google_sheet',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Google Sheet Link'),
        ),
    ]