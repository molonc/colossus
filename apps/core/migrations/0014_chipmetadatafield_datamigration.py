# -*- coding: utf-8 -*-
# created by jngo
from __future__ import unicode_literals

from django.db import migrations, models


def populate_metadatafield_from_existing_chipregionmetadata_fields(apps, schema_editor):
    ChipRegionMetadata = apps.get_model('core', 'ChipRegionMetadata')
    MetadataField = apps.get_model('core', 'MetadataField')

    for chipregionmetadata in ChipRegionMetadata.objects.all():
        chipregionmetadata.metadata_field = MetadataField.objects.get(field=chipregionmetadata.metadata_field_old)
        chipregionmetadata.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_chipmetadata_field_foreignkey_create'),
    ]

    operations = [
        migrations.RunPython(populate_metadatafield_from_existing_chipregionmetadata_fields),
    ]