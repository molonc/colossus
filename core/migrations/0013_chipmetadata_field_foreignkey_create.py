# -*- coding: utf-8 -*-
# created by jngo
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20170728_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='chipregionmetadata',
            name='metadata_field',
            field=models.ForeignKey(default="1", on_delete=django.db.models.deletion.CASCADE, to='core.MetadataField',
                                    verbose_name='Metadata key'),
            preserve_default=False,
        ),
    ]