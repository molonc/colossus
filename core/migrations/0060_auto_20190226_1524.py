# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-26 23:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_center'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dlpsequencing',
            unique_together=set([('library', 'sequencing_center', 'sequencing_instrument')]),
        ),
        migrations.AlterUniqueTogether(
            name='pbalsequencing',
            unique_together=set([('library', 'sequencing_center', 'sequencing_instrument')]),
        ),
        migrations.AlterUniqueTogether(
            name='tenxsequencing',
            unique_together=set([('library', 'sequencing_center', 'sequencing_instrument')]),
        ),
    ]