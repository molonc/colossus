"""
Created on May 31, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated Nov 21, 2017 by Spencer Vatrt-Watts (github.com/Spenca)
"""

from collections import OrderedDict

#============================
# Django imports
#----------------------------
from django.db import models
from django.shortcuts import render
from django.template.defaulttags import register


class Render(object):

    """
    Render the request with the given template.
    """

    def __init__(self, template):
        self.template = template

    def __call__(self, func):
        # @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            res = func(request, *args, **kwargs)
            # render it only if the response is a context dictionary
            if isinstance(res, dict):
                return render(request, self.template, res)
            else:
                return res
        return wrapper


def create_chrfield(name, max_length=50, blank=True, null=True, **kwargs):
    """wrap models.CharField for ease of use."""
    return models.CharField(
        name,
        max_length=max_length,
        blank=blank,
        null=null,
        **kwargs
        )


def create_textfield(name, max_length=5000, blank=True, null=True, **kwargs):
    """wrap models.TextField for ease of use."""
    return models.TextField(
        name,
        max_length=max_length,
        blank=blank,
        null=null,
        **kwargs
        )


def create_intfield(name, blank=True, null=True, **kwargs):
    """wrap models.IntegerField for ease of use."""
    return models.IntegerField(
        name,
        blank=blank,
        null=null,
        **kwargs
        )


def create_pathfield(name, max_length=250, blank=True, null=True, **kwargs):
    """wrap models.CharField for ease of use."""
    return models.CharField(
        name,
        max_length=max_length,
        blank=blank,
        null=null,
        **kwargs
        )


def upload_dlp_library_path(instance, filename):
    """make a proper /path/to/filename for uploaded files."""
    return "{0}/{1}/{2}".format(
        'library',      # leave this as 'library' for backwards compatibility
        instance.library.id,
        filename
        )

# Maintain migrations backwards compatibility
upload_path = upload_dlp_library_path


def upload_tenx_library_path(instance, filename):
    """Make a proper file path for uploading 10x library files."""
    return "{0}/{1}/{2}".format(
        'tenxlibrary',
        instance.library.id,
        filename
        )


class FieldValue(object):
    fields_to_exclude = ['ID']
    values_to_exclude = ['id']

    def get_fields(self):
        """get verbose names of all the fields."""
        field_names = [f.verbose_name for f in self._meta.fields
                       if f.verbose_name not in self.fields_to_exclude]
        return field_names

    def get_values(self):
        """get values of all the fields."""
        fields = [field.name for field in self._meta.fields]
        values = []
        for f in fields:
            if f not in self.values_to_exclude:
                a = "get_%s_display" % (f)
                if hasattr(self, a):
                    values.append(getattr(self, a)())
                else:
                    values.append(getattr(self, f))
        return values

    def get_field_values(self):
        """return a dict of key:values."""
        res = OrderedDict()
        for field in self._meta.fields:
            field_verbose_name = field.verbose_name
            field_name = field.name
            if field_verbose_name not in self.fields_to_exclude:
                a = "get_%s_display" % (field_name)
                if hasattr(self, a):
                    value = getattr(self, a)()
                else:
                    value = getattr(self, field_name)
                res[field_verbose_name] = value
        return res


class LibraryAssistant(object):
    gsc_required_fields = [
        (
            "sample",
            "Sample",
            "taxonomy_id",
            "Taxonomy ID",
            ),
        (
            "libraryconstructioninformation",
            "Library Construction Information",
            "library_type",
            "Library type",
            ),
        (
            "libraryconstructioninformation",
            "Library Construction Information",
            "library_construction_method",
            "Library construction method",
            ),
        (
            "libraryquantificationandstorage",
            "Library Quantification and Storage",
            "quantification_method",
            "Quantification method",
            ),
        (
            "libraryquantificationandstorage",
            "Library Quantification and Storage",
            "dna_concentration_nm",
            "DNA concentration (nM)",
            ),
        (
            "libraryquantificationandstorage",
            "Library Quantification and Storage",
            "storage_medium",
            "Storage medium",
            ),
        (
            "libraryquantificationandstorage",
            "Library Quantification and Storage",
            "size_range",
            "Size range",
            ),
        (
            "libraryquantificationandstorage",
            "Library Quantification and Storage",
            "average_size",
            "Average size",
            ),
        ]

    def has_library_sample_detail(self):
        if self.__class__.__name__ == 'DlpLibrary':
            return hasattr(self, 'dlplibrarysampledetail')
        elif self.__class__.__name__ == 'PbalLibrary':
            return hasattr(self, 'pballibrarysampledetail')
        elif self.__class__.__name__ == 'TenxLibrary':
            return hasattr(self, 'tenxlibrarysampledetail')

    def has_library_construction_information(self):
        if self.__class__.__name__ == 'DlpLibrary':
            return hasattr(self, 'dlplibraryconstructioninformation')
        elif self.__class__.__name__ == 'PbalLibrary':
            return hasattr(self, 'pballibraryconstructioninformation')
        elif self.__class__.__name__ == 'TenxLibrary':
            return hasattr(self, 'tenxlibraryconstructioninformation')

    def has_library_quantification_and_storage(self):
        if self.__class__.__name__ == 'DlpLibrary':
            return hasattr(self, 'dlplibraryquantificationandstorage')
        elif self.__class__.__name__ == 'PbalLibrary':
            return hasattr(self, 'pballibraryquantificationandstorage')
        elif self.__class__.__name__ == 'TenxLibrary':
            return hasattr(self, 'tenxlibraryquantificationandstorage')

    def get_missing_gsc_required_fields(self):
        missing_required_fields = []
        get_value = lambda related_obj, field: getattr(
            getattr(self, related_obj), field
            )
        for i in self.gsc_required_fields:
            related_obj = i[0]
            obj_verbose_name = i[1]
            field = i[2]
            field_verbose_name = i[3]
            try:
                value = get_value(related_obj, field)
            # self might not have the related_obj yet.
            except:
                missing_required_fields.append(
                    (obj_verbose_name, field_verbose_name)
                    )
            if not value:
                missing_required_fields.append(
                    (obj_verbose_name, field_verbose_name)
                    )
        return missing_required_fields

    def is_sequenced(self):
        if self.__class__.__name__ == 'DlpLibrary':
            return any([s.dlplane_set.filter(path_to_archive__isnull=False) for s in self.dlpsequencing_set.all()])
        elif self.__class__.__name__ == 'PbalLibrary':
            return any([s.pballane_set.filter(path_to_archive__isnull=False) for s in self.pbalsequencing_set.all()])
        elif self.__class__.__name__ == 'TenxLibrary':
            return any([s.tenxlane_set.filter(path_to_archive__isnull=False) for s in self.tenxsequencing_set.all()])
