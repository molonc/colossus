"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

#============================
# Django rest framework imports
#----------------------------
from rest_framework import serializers

#============================
# App imports
#----------------------------
from core.models import (
    Library,
    Sample,
    SublibraryInformation,
    Sequencing,
    SequencingDetail
)

#============================
# Other imports
#----------------------------


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Sample
        fields = (
            'anonymous_patient_id',
            'cell_line_id',
            'sample_id',
            'sample_type',
            'taxonomy_id',
        )


class SublibraryInformationSerializer(serializers.ModelSerializer):
    sample_id = SampleSerializer(read_only=True)
    class Meta:
        model=SublibraryInformation
        fields = (
            'sample_id',
            'row',
            'column',
            'img_col',
            'condition',
            'index_i5',
            'index_i7',
            'primer_i5',
            'primer_i7',
            'pick_met',
        )


class SequencingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingDetail
        fields = (
            'flow_cell_id',
            'gsc_library_id',
            'sequencing_center',
        )


class SequencingSerializer(serializers.ModelSerializer):
    sequencingdetail = SequencingDetailSerializer(read_only=True)
    library = serializers.SlugRelatedField(read_only=True, slug_field='pool_id')
    class Meta:
        model = Sequencing
        fields = (
            'library',
            'adapter',
            'pool_id',
            'read_type',
            'index_read_type',
            'sequencing_instrument',
            'submission_date',
            'sequencingdetail'
        )


class LibrarySerializer(serializers.ModelSerializer):
    sample = SampleSerializer(read_only=True)
    sequencing_set = SequencingSerializer(many=True, read_only=True)
    sublibraryinformation_set = SublibraryInformationSerializer(many=True,
        read_only=True)
    class Meta:
        model=Library
        fields = (
            'pool_id',
            'jira_ticket',
            'num_sublibraries',
            'description',
            'sample',
            'result',
            'relates_to',
            'sequencing_set',
            'sublibraryinformation_set',
        )


class LibrarySerializerBrief(LibrarySerializer):
    class Meta:
        model=Library
        fields = (
            'pool_id',
            'jira_ticket',
            'num_sublibraries',
            'description',
            'sample',
            'result',
            'relates_to',
            'sequencing_set'
        )
