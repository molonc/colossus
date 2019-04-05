from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from pbal.forms import (
    PbalLibraryForm,
    PbalLibrarySampleDetailInlineFormset,
    PbalLibraryConstructionInfoInlineFormset,
    PbalLibraryQuantificationAndStorageInlineFormset,
    PbalSequencingForm, PbalLaneForm, PlateForm)

from core.helpers import Render

from core.views import (
    LibraryList,
    LibraryDetail,
    LibraryDelete,
    LibraryCreate,
    LibraryUpdate,
    SequencingList,
    SequencingCreate, SequencingUpdate, SequencingDelete, LaneCreate, LaneUpdate, SequencingDetail, LaneDelete)

from .models import PbalLibrary, PbalSequencing, PbalLane, Plate


class PbalLibraryList(LibraryList):
    order = 'sample_id'
    library_class = PbalLibrary
    library_type = 'pbal'


class PbalLibraryDetail(LibraryDetail):
    library_class = PbalLibrary
    library_type = 'pbal'


class PbalLibraryDelete(LibraryDelete):
    library_class = PbalLibrary
    library_type = 'pbal'


class PbalLibraryCreate(LibraryCreate):
    lib_form_class = PbalLibraryForm
    libdetail_formset_class = PbalLibrarySampleDetailInlineFormset
    libcons_formset_class = PbalLibraryConstructionInfoInlineFormset
    libqs_formset_class = PbalLibraryQuantificationAndStorageInlineFormset
    library_type = 'pbal'


class PbalLibraryUpdate(LibraryUpdate):
    library_class = PbalLibrary
    lib_form_class = PbalLibraryForm
    libdetail_formset_class = PbalLibrarySampleDetailInlineFormset
    libcons_formset_class = PbalLibraryConstructionInfoInlineFormset
    libqs_formset_class = PbalLibraryQuantificationAndStorageInlineFormset
    library_type = 'pbal'


class PbalSequencingList(SequencingList):
    sequencing_class = PbalSequencing
    library_type = 'pbal'


class PbalSequencingCreate(SequencingCreate):
    library_class = PbalLibrary
    sequencing_class = PbalSequencing
    form_class = PbalSequencingForm
    library_type = 'pbal'


class PbalSequencingUpdate(SequencingUpdate):
    sequencing_class = PbalSequencing
    form_class = PbalSequencingForm
    library_type = 'pbal'


class PbalSequencingDelete(SequencingDelete):
    sequencing_class = PbalSequencing
    library_type = 'pbal'


class PbalSequencingDetail(SequencingDetail):
    sequencing_class = PbalSequencing
    library_type = 'pbal'


class PbalLaneCreate(LaneCreate):
    sequencing_class = PbalSequencing
    form_class = PbalLaneForm
    library_type = 'pbal'


class PbalLaneUpdate(LaneUpdate):
    lane_class = PbalLane
    form_class = PbalLaneForm
    library_type = 'pbal'



class PbalLaneDelete(LaneDelete):
    lane_class = PbalLane
    library_type = 'pbal'


#============================
# Plate views
#----------------------------
@Render("core/plate_create.html")
@login_required
def plate_create(request, from_library=None):
    if from_library:
        library = get_object_or_404(PbalLibrary, pk=from_library)
    else:
        library = None

    if request.method == 'POST':
        form = PlateForm(request.POST)
        if form.is_valid():
            instance = form.save()
            msg = "Successfully created the plate."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.library.get_absolute_url())
        else:
            msg = "Failed to create the plate. Please fix the errors below."
            messages.error(request, msg)
    else:
        form = PlateForm()

    context = {
        'form': form,
        'library': str(library),
        'library_id': from_library,
    }
    return context


@Render("core/plate_update.html")
@login_required
def plate_update(request, pk):
    plate = get_object_or_404(Plate, pk=pk)

    if request.method == 'POST':
        form = PlateForm(request.POST, instance=plate)
        if form.is_valid():
            instance = form.save()
            msg = "Successfully updated the plate."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.library.get_absolute_url())
        else:
            msg = "Failed to update the plate. Please fix the errors below."
            messages.error(request, msg)
    else:
        form = PlateForm(instance=plate)

    context = {
        'form': form,
        'library': plate.library,
        'library_id': plate.library_id,
        'pk': pk,
    }
    return context


@Render("core/plate_delete.html")
@login_required
def plate_delete(request, pk):
    plate = get_object_or_404(Plate, pk=pk)
    library = plate.library

    if request.method == 'POST':
        plate.delete()
        msg = "Successfully deleted the Plate."
        messages.success(request, msg)
        return HttpResponseRedirect(library.get_absolute_url())

    context = {
        'plate': plate,
        'pk': pk,
        'library_id': library.id,
    }
    return context
