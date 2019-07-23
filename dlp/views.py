import os, subprocess, io

import pandas as pd
from django.contrib.auth.decorators import login_required

from colossus import settings
from core.forms import GSCFormDeliveryInfo, GSCFormSubmitterInfo
from core.models import MetadataField, SublibraryInformation
from core.utils import generate_gsc_form
from dlp.models import *
from dlp.forms import *
from sisyphus.models import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.views.generic import TemplateView
from colossus.settings import LOGIN_URL
from core.views import (
    LibraryList,
    LibraryDetail,
    LibraryDelete,
    LibraryCreate,
    LibraryUpdate,
    SequencingCreate,
    SequencingDetail,
    SequencingUpdate,
    SequencingDelete,
    LaneCreate,
    LaneUpdate,
    LaneDelete,
    SequencingList
)

import collections

class DlpLibraryList(LibraryList):
    order = 'pool_id'
    library_class = DlpLibrary
    library_type = 'dlp'

    def get_context_data(self):
        all_libraries = self.library_class.objects.all().order_by(self.order)

        for library in all_libraries:
            library.num_sequencings = library.dlpsequencing_set.count()
            library.max_sequencing_analysis = 0
            for analysis in library.dlpanalysisinformation_set.all():
                if analysis.sequencings.count() > library.max_sequencing_analysis:
                    library.max_sequencing_analysis = analysis.sequencings.count()

        context = {
            'libraries': all_libraries,
            'library_type': self.library_type,
        }
        return context

class DlpSequencingDetail(SequencingDetail):
    sequencing_class = DlpSequencing
    library_type = 'dlp'

class DlpLibraryDetail(LibraryDetail):
    def get(self, request, pk):
        library = get_object_or_404(DlpLibrary, pk=pk)
        library_type = 'dlp'
        analyses = DlpAnalysisInformation.objects.filter(sequencings__in=library.dlpsequencing_set.all()).distinct()
        sublibinfo = SublibraryInformation()
        fields = MetadataField.objects.distinct().filter(chipregionmetadata__chip_region__library=library).values_list('field', flat=True).distinct()
        metadata_dict = collections.OrderedDict()

        for chip_region in library.chipregion_set.all().order_by('region_code'):
            metadata_set = chip_region.chipregionmetadata_set.all()
            d1 = {}

            for metadata in metadata_set:
                d1[metadata.metadata_field.field] = metadata.metadata_value
            row = []

            for field in fields:
                # Check that columns named in "fields" exist, else populate with "" if no entry in row for that particular metadata column
                # then adding it to a metadata dictionary with other rows
                if field not in d1.keys():
                    d1[field] = ""
                row.append(d1[field])
            metadata_dict[chip_region.region_code] = row

        return self.get_context_and_render(request, library, library_type, analyses, sublibinfo.get_fields(), metadata_dict, fields)

    def sort_library_order(self, library):
        new_library_order = ['Description', 'Result', 'Title', 'Jira ticket', 'Quality', 'Chip ID', 'Number of sublibraries']
        sorted_library_dict = OrderedDict()
        library_dict_original = dict(library.get_field_values())
        for x in new_library_order:
            sorted_library_dict[x] = library_dict_original[x]
        return sorted_library_dict

class DlpLibraryUpdate(LibraryUpdate):
    library_class = DlpLibrary
    lib_form_class = DlpLibraryForm
    libdetail_formset_class = DlpLibrarySampleDetailInlineFormset
    libcons_formset_class = DlpLibraryConstructionInfoInlineFormset
    libqs_formset_class = DlpLibraryQuantificationAndStorageInlineFormset
    library_type = 'dlp'

class DlpLibraryDelete(LibraryDelete):
    library_class = DlpLibrary
    library_type = 'dlp'


class DlpLibraryCreate(LibraryCreate):
    lib_form_class = DlpLibraryForm
    libdetail_formset_class = DlpLibrarySampleDetailInlineFormset
    libcons_formset_class = DlpLibraryConstructionInfoInlineFormset
    libqs_formset_class = DlpLibraryQuantificationAndStorageInlineFormset
    library_type = 'dlp'


class DlpSequencingList(SequencingList):
    sequencing_class = DlpSequencing
    library_type = 'dlp'

class DlpSequencingCreate(SequencingCreate):
    library_class = DlpLibrary
    sequencing_class = DlpSequencing
    form_class = DlpSequencingForm
    library_type = 'dlp'

class DlpSequencingUpdate(SequencingUpdate):
    sequencing_class = DlpSequencing
    form_class = DlpSequencingForm
    library_type = 'dlp'


class DlpSequencingDelete(SequencingDelete):
    sequencing_class = DlpSequencing
    library_type = 'dlp'

class DlpSequencingCreateGSCFormView(LoginRequiredMixin, TemplateView):
    login_url = LOGIN_URL
    template_name = "core/sequencing_create_gsc_form.html"

    def get_context_data(self, pk):
        context = {
            'pk': pk,
            'delivery_info_form': GSCFormDeliveryInfo(),
            'submitter_info_form': GSCFormSubmitterInfo(),
            'library_type': 'dlp',
        }
        return context

    def get(self, request, pk):
        context = self.get_context_data(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk):
        sequencing = get_object_or_404(DlpSequencing, pk=pk)
        context = self.get_context_data(pk)
        delivery_info_form = GSCFormDeliveryInfo(request.POST)
        submitter_info_form = GSCFormSubmitterInfo(request.POST)
        if delivery_info_form.is_valid() and submitter_info_form.is_valid():
            key = "gsc_form_metadata_%s" % pk
            request.session[key] = request.POST
            msg = "Successfully started downloading the GSC submission form."
            messages.success(request, msg)
            return HttpResponseRedirect(sequencing.get_absolute_url())
        else:
            context['delivery_info_form'] = delivery_info_form
            context['submitter_info_form'] = submitter_info_form
            msg = "please fix the errors below."
            messages.error(request, msg)
        return render(request, self.template_name, context)


@login_required
def dlp_sequencing_get_gsc_form(request, pk):
    key = "gsc_form_metadata_%s" % pk
    metadata = request.session.pop(key)
    ofilename, buffer = generate_gsc_form(pk, metadata)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=%s' % ofilename
    return response


@login_required
def library_id_to_pk_redirect(request, pool_id):
    pk = get_object_or_404(DlpLibrary, pool_id=pool_id).pk
    return redirect("/dlp/library/{}".format(pk))

class DlpLaneCreate(LaneCreate):
    sequencing_class = DlpSequencing
    form_class = DlpLaneForm
    library_type = 'dlp'

class DlpLaneUpdate(LaneUpdate):
    lane_class = DlpLane
    form_class = DlpLaneForm
    library_type = 'dlp'

class DlpLaneDelete(LaneDelete):
    lane_class = DlpLane
    library_type = 'dlp'

#============================
# Summary view
#----------------------------
@Render("core/summary.html")
def dlp_summary_view(request):

    library_per_sample_count = {s.sample_id : s.dlplibrary_set.count() for s in Sample.objects.all()}

    sublibrary_per_sample_count = {s.sample_id : s.sublibraryinformation_set.count() for s in Sample.objects.all()}

    context ={
        'library_per_sample': library_per_sample_count,
        'sublibrary_per_sample': sublibrary_per_sample_count,
        'total_sublibs': SublibraryInformation.objects.count(),
        'total_libs': DlpLibrary.objects.count(),
        'samples':Sample.objects.all().order_by('sample_id'),
    }
    return context

def dlp_get_filtered_sublib_count(sublibs):
    unfiltered_count = sublibs.count()

    # wells to filter out
    blankwells_count = sublibs.filter(spot_well='nan').count()

    # final count
    filtered_count = unfiltered_count - blankwells_count
    return filtered_count


def dlp_get_cell_graph(request):

    data = []
    libs = DlpLibrary.objects.filter(dlpsequencing__isnull=False, sublibraryinformation__isnull=False).distinct()

    for lib in libs:
        lib_info = {}
        lib_info['jira_ticket'] = lib.jira_ticket
        lib_info['pool_id'] = lib.pool_id
        lib_info['count'] = dlp_get_filtered_sublib_count(lib.sublibraryinformation_set)
        lib_info['id'] = lib.pk

        for sequencing in lib.dlpsequencing_set.all():
            lib_info['submission_date'] = sequencing.submission_date
            data.append(lib_info)

    df = pd.DataFrame(data)
    # TODO: change time to just only include date
    today = str(timezone.now().strftime('%Y-%m-%d'))
    ofilename = os.path.join("cell_count-" + today + ".csv")
    output_csv_path = os.path.join(settings.MEDIA_ROOT, ofilename)
    df.to_csv(output_csv_path, index=False)


    rscript_path = os.path.join(settings.BASE_DIR, "scripts", "every_cell_count_plot.R")
    cmd = "Rscript {rscript} {input_csv} {media_dir}output.pdf".format(rscript=rscript_path, input_csv=output_csv_path, media_dir=settings.MEDIA_ROOT)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r_stdout, r_stderr = p.communicate()
    if p.returncode != 0:
        raise Exception('cmd {} failed\nstdout:\n{}\nstderr:\n{}\n'.format(cmd, r_stdout, r_stderr))

    output_plots_path = os.path.join(settings.MEDIA_ROOT, "output.pdf")

    with open(output_plots_path, 'rb') as f:
        plots_pdf = f.read()
        response = HttpResponse(plots_pdf, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % ("cell-count_" + today + ".pdf")
    os.remove(output_csv_path)
    os.remove(output_plots_path)

    return response

def export_sublibrary_csv(request,pk):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Sublibrary-info.csv"'
    dlp = DlpLibrary.objects.get(id=pk)
    df = pd.DataFrame(list(dlp.sublibraryinformation_set.all().values()))
    df = df.assign(Sublibrary_information = pd.Series([x.get_sublibrary_id()for x in dlp.sublibraryinformation_set.all()], index=df.index))
    df.to_csv(response)
    return response

