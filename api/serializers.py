"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""

#============================
# Django rest framework imports
#----------------------------
from rest_framework import serializers

#============================
# App imports
#----------------------------
from core.models import (
    DlpLibrary,
    Sample,
    SublibraryInformation,
    DlpSequencing,
    DlpSequencingDetail,
    DlpLane,
    ChipRegionMetadata,
    MetadataField,
    ChipRegion
)

from sisyphus.models import DlpAnalysisInformation, ReferenceGenome, AnalysisRun, DlpAnalysisVersion

#============================
# Other imports
#----------------------------


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = (
            'anonymous_patient_id',
            'cell_line_id',
            'sample_id',
            'sample_type',
            'taxonomy_id',
            'xenograft_id'
        )


class LaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpLane
        fields = (
            'sequencing',
            'flow_cell_id',
            'path_to_archive',
        )


class SequencingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpSequencingDetail
        fields = (
            'gsc_library_id',
            'sequencing_center',
            'rev_comp_override',
        )


class SequencingSerializer(serializers.ModelSerializer):
    dlpsequencingdetail = SequencingDetailSerializer(read_only=True)
    library = serializers.SlugRelatedField(read_only=True, slug_field='pool_id')
    dlplane_set = LaneSerializer(many=True, read_only=True)
    class Meta:
        model = DlpSequencing
        fields = (
            'library',
            'adapter',
            'read_type',
            'index_read_type',
            'sequencing_instrument',
            'submission_date',
            'dlplane_set',
            'dlpsequencingdetail',
        )


class LibrarySerializer(serializers.ModelSerializer):
    sample = SampleSerializer(read_only=True)
    dlpsequencing_set = SequencingSerializer(many=True, read_only=True)
    class Meta:
        model = DlpLibrary
        fields = (
            'id',
            'pool_id',
            'jira_ticket',
            'num_sublibraries',
            'description',
            'sample',
            'result',
            'relates_to',
            'dlpsequencing_set',
            'title',
            'quality'
        )

class SublibraryInformationSerializer(serializers.ModelSerializer):
    sample_id = SampleSerializer(read_only=True)
    library = LibrarySerializer(read_only=True)

    class Meta:
        model = SublibraryInformation
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
            'library',
        )


class ReferenceGenomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceGenome
        fields = (
            'reference_genome',
        )


class AnalysisRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRun
        fields = (
            'id',
            'run_status',
            'log_file',
            'last_updated'
        )


class DlpAnalysisVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpAnalysisVersion
        fields = (
            'version',
        )


class AnalysisInformationSerializer(serializers.ModelSerializer):
    reference_genome = ReferenceGenomeSerializer(read_only=True)
    version = DlpAnalysisVersionSerializer(read_only=True)

    class Meta:
        model = DlpAnalysisInformation
        fields = (
            'id',
            'library',
            'priority_level',
            'analysis_jira_ticket',
            'version',
            'analysis_submission_date',
            'sequencings',
            'reference_genome',
            'analysis_run',
            'aligner',
            'smoothing',
            'sftp_path',
            'blob_path'
        )

    def create(self, validated_data):
        validated_data['analysis_run'] = AnalysisRun.objects.create()
        # Remove many to many field
        sequencings = validated_data.pop('sequencings')
        instance = DlpAnalysisInformation.objects.create(**validated_data)
        instance.full_clean()
        instance.save()

        # Re-add many to many field
        instance.sequencings = sequencings
        instance.save()
        return instance


class MetadataSerializer(serializers.ModelSerializer):

    class Meta:
        model = MetadataField
        fields = (
            '__all__'
        )


class ChipRegionMetadataSerializer(serializers.ModelSerializer):
    metadata_field = MetadataSerializer(read_only=True)
    metadata_field = metadata_field['field']._field

    class Meta:
        model = ChipRegionMetadata
        fields = (
            'metadata_field',
            'metadata_value',
        )


class ChipRegionSerializer(serializers.ModelSerializer):
    chipregionmetadata_set = ChipRegionMetadataSerializer(read_only=True,many=True)
    jira_ticket = serializers.CharField(source='library.jira_ticket')
    class Meta:
        model = ChipRegion
        fields = (
            'jira_ticket',
            'library',
            'region_code',
            'chipregionmetadata_set'
        )