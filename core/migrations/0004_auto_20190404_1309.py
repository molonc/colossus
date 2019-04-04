# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-04 20:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_table_pbal'),
        ('sisyphus', '0002_update_pbal_relationship'),
    ]

    state_operations = [
        migrations.DeleteModel('PbalLibrary'),
        migrations.DeleteModel('PbalLibrarySampleDetail'),
        migrations.DeleteModel('PbalLibraryConstructionInformation'),
        migrations.DeleteModel('PbalLibraryQuantificationAndStorage'),
        migrations.DeleteModel('PbalSequencing'),
        migrations.DeleteModel('PbalLane'),
        migrations.DeleteModel('Plate'),
        migrations.DeleteModel('HistoricalPbalLibrary'),
        migrations.DeleteModel('HistoricalPbalLibrarySampleDetail'),
        migrations.DeleteModel('HistoricalPbalLibraryConstructionInformation'),
        migrations.DeleteModel('HistoricalPbalLibraryQuantificationAndStorage'),
        migrations.DeleteModel('HistoricalPbalSequencing'),
        migrations.DeleteModel('HistoricalPbalLane'),
        migrations.DeleteModel('HistoricalPlate'),

    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations,
        )
    ]