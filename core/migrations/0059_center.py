import core.helpers
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q
import django.utils.timezone

#create table lll as (select * from core_dlpsequencing);
#update core_dlpsequencing s
#    set sequencing_center=t.sequencing_center
#    from lll t
#    where s.id=t.id;


def migrate(apps, schema_editor):
    Sequence = apps.get_model('core','DlpSequencing')

    c2 = 'UBCBRC'
    print("\nupdating to '%s';" % (c2))
    for s in Sequence.objects.filter( Q(sequencing_center='BRC')
                                    | Q(sequencing_center='ubcbrc') ):
        print("updating; id: {}; center: '{}';" . format(s.id,s.sequencing_center))
        s.sequencing_center = c2
        s.save()


#empty function, required to rollback migration
def do0(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    initial = True

    dependencies = [('core','0058_date')]

    operations = [
        migrations.RunPython(migrate,do0),
    ]
