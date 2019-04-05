from django.forms import inlineformset_factory, SelectDateWidget, ModelForm

from core.forms import LibraryForm, LibraryQuantificationAndStorageForm, SaveDefault, SequencingForm, LaneForm
from pbal.models import PbalLibrary, PbalLibraryQuantificationAndStorage, PbalLibrarySampleDetail, \
    PbalLibraryConstructionInformation, PbalSequencing, PbalLane, Plate


class PbalLibraryForm(LibraryForm):
    class Meta:
        model = PbalLibrary
        exclude = []
        labels = {
            'primary sample': ('*Sample'),
            'jira_ticket': ('*Jira Ticket'),
        }
        help_texts = {
            'sample': ('Sequencing ID (usually SA ID) of the sample composing the majority of the library.'),
            'jira_ticket': ('Jira Ticket.'),
        }



class PbalLibraryQuantificationAndStorageForm(LibraryQuantificationAndStorageForm):

    """
    Clean uploaded PBAL-related files.
    """

    class Meta(LibraryQuantificationAndStorageForm.Meta):
        model = PbalLibraryQuantificationAndStorage

PbalLibrarySampleDetailInlineFormset = inlineformset_factory(
    PbalLibrary,
    PbalLibrarySampleDetail,
    form = SaveDefault,
    can_delete = False,
    fields = "__all__",
    widgets = {
        'sample_spot_date': SelectDateWidget(
            years=range(2000,2020),
            empty_label=('year', 'month', 'day'),
        )
    }
)

PbalLibraryConstructionInfoInlineFormset =  inlineformset_factory(
    PbalLibrary,
    PbalLibraryConstructionInformation,
    form = SaveDefault,
    can_delete = False,
    fields = "__all__",
    widgets = {
        'submission_date': SelectDateWidget(
            years=range(2000,2020),
            empty_label=('year', 'month', 'day'),
        )
    }
)

PbalLibraryQuantificationAndStorageInlineFormset =  inlineformset_factory(
    PbalLibrary,
    PbalLibraryQuantificationAndStorage,
    form = PbalLibraryQuantificationAndStorageForm,
    can_delete = False,
    fields = "__all__",
)


class PbalSequencingForm(SequencingForm):
    class Meta(SequencingForm.Meta):
        model = PbalSequencing

class PbalLaneForm(LaneForm):
    class Meta(LaneForm.Meta):
        model = PbalLane
#===========================
# Plate form
#---------------------------
class PlateForm(ModelForm):
    class Meta:
        model = Plate
        fields = "__all__"
