# -*- coding: utf-8 -*-
# Mostly a copy of the previous migration, but adds a few overlooked
# statuses

from __future__ import print_function
from __future__ import unicode_literals
import sys
from django.db import migrations, models
from sisyphus.models import AnalysisRun

def reassign_analysisrun_statuses(apps, schema_editor):
    """Not reversable! Careful :o"""
    # Dictionary used to convert old statuses to new statuses
    status_map = {
        'A': AnalysisRun.ARCHIVING,
        'R': AnalysisRun.RUNNING,
        'E': AnalysisRun.ERROR,
        'W': AnalysisRun.IDLE,
        'F': AnalysisRun.COMPLETE,
        'C': AnalysisRun.COMPLETE,
        'Archiving': AnalysisRun.ARCHIVING,
        'Complete': AnalysisRun.COMPLETE,
        'Idle': AnalysisRun.IDLE,
        'Error': AnalysisRun.ERROR,
        'Running alignment': AnalysisRun.RUNNING,
        'Running align': AnalysisRun.RUNNING,
        'Running hmmcopy': AnalysisRun.RUNNING,
    }

    # Convert old statuses to new statuses
    old_statuses = status_map.keys()
    new_statuses = status_map.values()

    for run in AnalysisRun.objects.all():
        if run.run_status in old_statuses:
            # Old status found
            run.run_status = status_map[run.run_status]
            run.save()

            # Move on to the next run
            continue

        # Print a warning if we see an unrecognized status
        if run.run_status not in new_statuses:
            print("Unrecognized status %s" % run.run_status, file=sys.stderr)


class Migration(migrations.Migration):

    dependencies = [
        ('sisyphus', '0019_change_run_status_names_20180820_1118'),
    ]

    operations = [
        migrations.RunPython(reassign_analysisrun_statuses),
    ]
