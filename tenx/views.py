from django.contrib.auth.decorators import login_required

from tenx.models import *
from tenx.forms import *
from tenx.utils import tenxpool_naming_scheme
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
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
    LaneDelete
)



class TenxLibraryList(LibraryList):
    order = 'sample_id'
    library_class = TenxLibrary
    library_type = 'tenx'

@Render("core/tenxanalysis_list.html")
@login_required
def analys_list(request):
    context = {
        'analyses': TenxAnalysis.objects.all().order_by('id'),
    }
    return context

@Render("core/tenxanalysis_detail.html")
@login_required
def analysis_detail(request, pk):
    analysis = get_object_or_404(TenxAnalysis, pk=pk)
    context = {
        'analysis': analysis,
        'library': analysis.tenx_library,
        'sequencings': analysis.tenxsequencing_set
    }

    tenx_pools = list(map(lambda x: x.tenx_pool, analysis.tenxsequencing_set.all()))
    context['tenx_pools'] = tenx_pools
    return context

@login_required
def library_id_to_pk_redirect(request, pool_id):
    pk = get_object_or_404(TenxLibrary, name=pool_id).pk
    return redirect("/tenx/library/{}".format(pk))


class TenxLibraryDetail(LibraryDetail):
    library_class = TenxLibrary
    library_type = 'tenx'

    def get(self, request, pk):
        library = get_object_or_404(TenxLibrary, pk=pk)
        library_type = 'tenx'

        return self.get_context_and_render(
            request=request,
            library=library,
            library_type=library_type,
        )

class TenxLibraryDelete(LibraryDelete):
    library_class = TenxLibrary
    library_type = 'tenx'


class TenxLibraryCreate(LibraryCreate):
    lib_form_class = TenxLibraryForm
    libdetail_formset_class = TenxLibrarySampleDetailInlineFormset
    libcons_formset_class = TenxLibraryConstructionInfoInlineFormset
    libqs_formset_class = TenxLibraryQuantificationAndStorageInlineFormset
    library_type = 'tenx'


    def get_context_data(self, pk=None):
        context = super(TenxLibraryCreate, self).get_context_data(pk)
        return context


class TenxLibraryUpdate(LibraryUpdate):
    library_class = TenxLibrary
    lib_form_class = TenxLibraryForm
    libdetail_formset_class = TenxLibrarySampleDetailInlineFormset
    libcons_formset_class = TenxLibraryConstructionInfoInlineFormset
    libqs_formset_class = TenxLibraryQuantificationAndStorageInlineFormset
    library_type = 'tenx'

    def get_context_data(self, pk=None):
        context = super(TenxLibraryUpdate, self).get_context_data(pk)
        library = get_object_or_404(self.library_class, pk=pk)
        context['name'] = library.name

        return context


class TenxPoolList(LoginRequiredMixin, TemplateView):
    login_url = LOGIN_URL
    template_name = "core/tenx/tenxpool_list.html"

    def get_context_data(self):
        context = {
            'pools': TenxPool.objects.all().order_by('id'),
        }
        return context

class TenxPoolDetail(TemplateView):

    template_name = "core/tenx/tenxpool_detail.html"

    def get_context_data(self, pk):
        context = {
            'pool': get_object_or_404(TenxPool, pk=pk),
        }
        return context


class TenxPoolDelete(LoginRequiredMixin, TemplateView):
    login_url = LOGIN_URL
    template_name = "core/tenx/tenxpool_delete.html"

    def get_context_data(self, pk):
        context = {
            'pool': get_object_or_404(TenxPool, pk=pk),
            'pk': pk,
        }
        return context

    def post(self, request, pk):
        get_object_or_404(TenxPool, pk=pk).delete()
        msg = "Successfully deleted the Pool."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('tenx:pool_list'))


class TenxPoolCreate(LoginRequiredMixin,TemplateView):
    login_url = LOGIN_URL
    template_name = "core/tenx/tenxpool_create.html"

    def get_context_data(self):
        context = {
            'form': TenxPoolForm(),
            'tenxlibraries' : TenxLibrary.objects.all()
        }
        return context

    def post(self, request):
        form = TenxPoolForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.pool_name = tenxpool_naming_scheme(instance)
            instance.save()
            msg = "Successfully created the %s pool." % instance.pool_name
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            messages.info(request, form.errors)
            return HttpResponseRedirect(request.get_full_path())


class TenxPoolUpdate(LoginRequiredMixin, TemplateView):
    login_url = LOGIN_URL
    template_name = "core/tenx/tenxpool_update.html"

    def get_context_data(self, pk):
        pool_library = [l.pk for l in get_object_or_404(TenxPool, pk=pk).libraries.all()]
        context = {
            'pk': pk,
            'form': TenxPoolForm(instance=get_object_or_404(TenxPool, pk=pk)),
            'tenxlibraries': TenxLibrary.objects.all(),
            'pool_library' : pool_library
        }
        return context

    def post(self, request, pk):
        form = TenxPoolForm(request.POST, instance=get_object_or_404(TenxPool, pk=pk))
        if form.is_valid():
            instance = form.save(commit=False)
            form.save_m2m()
            instance.pool_name = tenxpool_naming_scheme(instance)
            instance.save()

            msg = "Successfully created the %s pool." % instance.pool_name
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            messages.info(request, form.errors)
            return HttpResponseRedirect(request.get_full_path())


class TenxSequencingList(TemplateView):
    login_url = LOGIN_URL
    template_name = "core/tenx/tenxsequencing_list.html"

    def get_context_data(self):
        context = {
            'sequencings': TenxSequencing.objects.all().order_by('id'),
        }
        return context

class TenxSequencingCreate(SequencingCreate):
    library_class = TenxLibrary
    sequencing_class = TenxSequencing
    form_class = TenxSequencingForm
    library_type = 'tenx'

class TenxSequencingDetail(SequencingDetail):
    sequencing_class = TenxSequencing
    library_type = 'tenx'

class TenxSequencingUpdate(SequencingUpdate):
    sequencing_class = TenxSequencing
    form_class = TenxSequencingForm
    library_type = 'tenx'

class TenxSequencingDelete(SequencingDelete):
    sequencing_class = TenxSequencing
    library_type = 'tenx'

class TenxLaneCreate(LaneCreate):
    sequencing_class = TenxSequencing
    form_class = TenxLaneForm
    library_type = 'tenx'

class TenxLaneUpdate(LaneUpdate):
    lane_class = TenxLane
    form_class = TenxLaneForm
    library_type = 'tenx'

class TenxLaneDelete(LaneDelete):
    lane_class = TenxLane
    library_type = 'tenx'


#============================
# TenxChip views
#----------------------------
class TenxChipCreate(LoginRequiredMixin, TemplateView):

    login_url = LOGIN_URL
    template_name = "core/tenx/tenxchip_create.html"

    def get_context_data(self, **kwargs):
        context = {
            "form" : TenxChipForm
        }
        return context

    def post(self, request):
        form = TenxChipForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            return render_to_response('my_template.html', {'form': form})


class TenxChipList(LoginRequiredMixin, TemplateView):

    login_url = LOGIN_URL
    template_name = "core/tenx/tenxchip_list.html"

    def get_context_data(self):
        context = {
            'chips': TenxChip.objects.all().order_by('id'),
        }
        return context


class TenxChipDetail(LoginRequiredMixin, TemplateView):

    login_url = LOGIN_URL
    template_name = "core/tenx/tenxchip_detail.html"

    def get_context_data(self, pk):
        context = {
            'chip': get_object_or_404(TenxChip, pk=pk),
            'pk': pk,
        }

        return context


class TenxChipUpdate(LoginRequiredMixin, TemplateView):

    login_url = LOGIN_URL
    template_name = "core/tenx/tenxchip_update.html"

    def get_context_data(self, pk):
        chip = get_object_or_404(TenxChip, pk=pk)
        form=TenxChipForm(instance=chip)
        context = {
            "form" : form,
            "pk" : pk
        }
        return  context

    def post(self, request, pk):
        chip = get_object_or_404(TenxChip, pk=pk)
        form = TenxChipForm(request.POST, instance=chip)

        if form.is_valid():
            form.save()
            msg = "Successfully updated the Chip."
            messages.success(request, msg)
            return HttpResponseRedirect(chip.get_absolute_url())

        msg = "Failed to update the Chip. Please fix the errors below."
        messages.error(request, msg)
        return self.get_context_and_render(request, form, pk=pk)



class TenxChipDelete(LoginRequiredMixin, TemplateView):

    login_url = LOGIN_URL
    template_name = "core/tenx/tenxchip_delete.html"

    def get_context_data(self, pk):
        context = {
            'chip': get_object_or_404(TenxChip, pk=pk),
        }
        return context

    def post(self, request, pk):
        get_object_or_404(TenxChip, pk=pk).delete()
        msg = "Successfully deleted the Chip."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('tenx:chip_list'))
