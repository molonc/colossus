import core.helpers
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q
import django.utils.timezone

from datetime import datetime
import dateutil.tz

#create table l01 as (select id, sequencing_date as dt from core_dlplane);
#create table ll as (select * from core_dlplane);
#update core_dlplane s
#    set sequencing_date=t.sequencing_date, path_to_archive=t.path_to_archive
#    from ll t
#    where s.id=t.id;


#191 AHTWGLAFXX /share/lustre/archive/single_cell_indexing/NextSeq/bcl/171124_NS500668_0278_AHTWGLAFXX
#237 AHVKFFAFXX /share/lustre/archive/single_cell_indexing/NextSeq/bcl/180112_NS500668_0308_AHVKFFAFXX

path_map = {
     191: '/share/lustre/archive/single_cell_indexing/NextSeq/bcl/171124_NS500668_0278_AHTWGLAFXX/'
    ,237: '/share/lustre/archive/single_cell_indexing/NextSeq/bcl/180112_NS500668_0308_AHVKFFAFXX/'
}

def get_date(str):
    """
    input string format:
        /ccc/cccc/.../ccc/yyMMdd_cccc_ccc_..._cccc_ccc/
        ^^^ many subdirs     ^ date is first, separator is '_'
            date is last            could be many
        date part is in '%y%m%d' format
    output date format:
        'yyyy-MM-dd hh:mm:ss'
    """
    if str is None: return None
    a = str.split('/')
    if len(a) < 1: return None
    if len(a[-1]) > 0:
        b = a[-1]
    else:
        if len(a) < 2: return None
        b = a[-2]
    d = b.split('_')
    if len(d) < 1: return None
    res = None
    try:
        #res = datetime.datetime(datetime.strptime(d[0],"%y%m%d"),tzinfo=tzoffset(None,7*3600))
        res = datetime.strptime(d[0],"%y%m%d")
    except:
        print("format error; {}; {};" . format(d[0],str))
        pass

    return res

def migrate(apps, schema_editor):
    Sequence = apps.get_model('core','DlpSequencing')
    Lane     = apps.get_model('core','DlpLane')

    for (k,v) in path_map.iteritems():
        l = Lane.objects.get(pk=k)
        print("setting path id=%i; val=%s;" % (k,v))
        l.path_to_archive = v
        l.save()

    for l in Lane.objects.filter( (  Q(sequencing__sequencing_center='BRC')
                                   | Q(sequencing__sequencing_center='UBCBRC')
                                   | Q(sequencing__sequencing_center='ubcbrc') )
                                #& Q(sequencing_date__isnull=True)
                                & Q(path_to_archive__isnull=False)
                                ):
        dt = get_date(l.path_to_archive)
        if dt != None:
            #print("id: {}; upd to date: {}; {};" . format(l.id,dt,l.path_to_archive))
            if   l.sequencing_date is None  \
              or dt.date() != l.sequencing_date.date():
                print("date changing; {}; old {}; new {};" . format(l.id,l.sequencing_date,dt))
                l.sequencing_date = dt
                l.save()


#empty function, required to rollback migration
def do0(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    initial = True

    dependencies = [('core','0057_jirauser')]

    operations = [
        migrations.RunPython(migrate,do0),
    ]
