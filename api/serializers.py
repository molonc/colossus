"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""

#============================
# Django rest framework imports
#----------------------------
import collections
import re

from rest_framework import serializers

#============================
# App imports
#----------------------------
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from core.models import (
    Sample,
    AdditionalSampleInformation,
    SublibraryInformation,
    ChipRegionMetadata,
    MetadataField,
    ChipRegion,
    JiraUser,
    Project,
    DoubletInformation)

from dlp.models import (
    DlpLibraryConstructionInformation,
    DlpLibrarySampleDetail,
    DlpSequencing,
    DlpLane,
    DlpLibrary,
    DlpLibraryQuantificationAndStorage)

from tenx.models import *

from sisyphus.models import (
    DlpAnalysisInformation,
    ReferenceGenome,
    AnalysisRun,
    DlpAnalysisVersion,
    )


#============================
# Other imports
#----------------------------


class AdditionalSampleInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalSampleInformation
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id',
            'name',
            'description',
            'dlplibrary_set',
            'pballibrary_projects',
            'tenxlibrary_set'
        )


class SampleSerializer(serializers.ModelSerializer):
    additionalsampleinformation = (
        AdditionalSampleInformationSerializer(read_only=True)
    )
    class Meta:
        model = Sample
        fields = (
            'id',
            'anonymous_patient_id',
            'cell_line_id',
            'sample_id',
            'sample_type',
            'taxonomy_id',
            'xenograft_id',
            'dlplibrary_set',
            'tenxlibrary_set',
            'additionalsampleinformation',
        )


class TenxAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxAnalysis
        fields = (
            'id',
            'version',
            'jira_ticket',
            'run_status',
            'last_updated_date',
            'submission_date',
            'description',
            'tenx_library',
            'tenxsequencing_set',
        )

class LaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpLane
        fields = (
            'id',
            'sequencing',
            'flow_cell_id',
            'sequencing_date',
            'path_to_archive',
        )



class SequencingSerializer(serializers.ModelSerializer):
    library = serializers.SlugRelatedField(read_only=True, slug_field='pool_id')
    class Meta:
        model = DlpSequencing
        fields = [
            "id",
            "library",
            "dlplane_set",
            "rev_comp_override",
            "adapter",
            "format_for_data_submission",
            "index_read_type",
            "index_read1_length",
            "index_read2_length",
            "read_type",
            "read1_length",
            "read2_length",
            "sequencing_instrument",
            "sequencing_output_mode",
            "short_description_of_submission",
            "submission_date",
            "number_of_lanes_requested",
            "lane_requested_date",
            "gsc_library_id",
            "sequencer_id",
            "sequencing_center",
            "sequencer_notes",
            "relates_to",
            "dlplane_set"
        ]


class TagSerializerField(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id',
            'name',
        )


class DlpLibraryConstructionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpLibraryConstructionInformation
        fields = '__all__'


class DlpLibrarySampleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpLibrarySampleDetail
        fields = '__all__'

class DlpLibraryQuantificationAndStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpLibraryQuantificationAndStorage
        fields = '__all__'

class DoubletInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubletInformation
        exclude = ['library']


class LibrarySerializer(serializers.ModelSerializer):
    sample = SampleSerializer()
    dlplibraryconstructioninformation = DlpLibraryConstructionInformationSerializer()
    dlplibrarysampledetail = DlpLibrarySampleDetailSerializer()
    dlplibraryquantificationandstorage = DlpLibraryQuantificationAndStorageSerializer()
    projects = TagSerializerField(read_only=True, many=True)
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
            'relates_to_dlp',
            'relates_to_tenx',
            'dlpsequencing_set',
            'title',
            'quality',
            'failed',
            'projects',
            'dlplibraryconstructioninformation',
            'dlplibrarysampledetail',
            'dlplibraryquantificationandstorage',
            'sublibraryinformation_set',
            'exclude_from_analysis',
        )
    def to_representation(self, instance):
        value = super(LibrarySerializer, self).to_representation(instance)

        try:
            doublet = instance.doubletinformation
            value['doubletinformation'] = {
                    'live' : { 'Single' : doublet.live_single, 'Doublet' : doublet.live_doublet, 'Other' : doublet.live_gt_doublet},
                    'dead' : { 'Single' : doublet.dead_single, 'Doublet' : doublet.dead_doublet, 'Other' : doublet.dead_gt_doublet},
                    'other': { 'Single' : doublet.other_single, 'Doublet' : doublet.other_doublet, 'Other' : doublet.other_gt_doublet},
                }
        except: value['doubletinformation'] = {}

        for chip_region in instance.chipregion_set.all().order_by('region_code'):
            metadata_set = chip_region.chipregionmetadata_set.all()
            d1 = {}
            for metadata in metadata_set:
                d1[metadata.metadata_field.field] = metadata.metadata_value
            value['metadata'] = d1
        return value

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

    def to_representation(self, instance):
        value = super(SublibraryInformationSerializer, self).to_representation(instance)
        if instance.chip_region:
            value["metadata"] = {"region_code" : instance.chip_region.region_code}
            for metadata in instance.chip_region.chipregionmetadata_set.all():
                value["metadata"][metadata.metadata_field.field] = metadata.metadata_value
        value["cell_id"] = instance.get_sublibrary_id()
        return value

class SublibraryInformationSerializerBrief(serializers.ModelSerializer):
    class Meta:
        model = SublibraryInformation
        fields = '__all__'


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
            'sftp_path',
            'blob_path',
            'dlpanalysisinformation',
            'last_updated'
        )

    def save(self, **kwargs):
        """Make sure associated analysis info is saved."""
        # Save the analysis run
        analysis_run = super(AnalysisRunSerializer, self).save(**kwargs)

        # Update the analysis information
        related_dlp_analysis_info = (
            self.validated_data.get('dlpanalysisinformation', None))

        if related_dlp_analysis_info is not None:
            related_dlp_analysis_info.analysis_run = analysis_run
            related_dlp_analysis_info.save()

        # Return the analysis run we saved
        return analysis_run


class AnalysisInformationSerializer(serializers.ModelSerializer):
    library = LibrarySerializer(read_only=True)
    analysis_run = AnalysisRunSerializer(read_only=True)
    reference_genome = ReferenceGenomeSerializer(read_only=True)
    version = serializers.CharField(source='version.version')

    class Meta:
        model = DlpAnalysisInformation
        fields = (
            'id',
            'library',
            'montage_status',
            'priority_level',
            'analysis_jira_ticket',
            'version',
            'analysis_submission_date',
            'sequencings',
            'reference_genome',
            'analysis_run',
            'aligner',
            'smoothing',
            'lanes',
        )

    def create(self, validated_data):
        validated_data['analysis_run'] = AnalysisRun.objects.create()
        # Remove many to many field
        sequencings = validated_data.pop('sequencings')
        for sequencing in sequencings:
            if not sequencing.library == validated_data["library"]:
                raise ValidationError("Selected sequencings must belong to selected library")
        lanes = validated_data.pop('lanes')

        instance = DlpAnalysisInformation.objects.create(**validated_data)
        instance.full_clean()
        instance.save()

        # Re-add many to many field
        instance.sequencings = sequencings
        instance.lanes = lanes
        instance.save()
        return instance


class AnalysisInformationCreateSerializer(serializers.ModelSerializer):
    version = serializers.CharField(source='version.version')

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
            'montage_status',
            'aligner',
            'smoothing',
            'lanes',
        )

    def create(self, validated_data):
        """Handle version field in here."""
        validated_data['version'], _ = (
            DlpAnalysisVersion.objects.get_or_create(
                version=validated_data['version']['version'],
            )
        )

        # Remove many-to-many field and re-add in after we have a pk for
        # our instance (required for many-to-many field)
        sequencings = validated_data.pop('sequencings')
        for sequencing in sequencings:
            if not sequencing.library == validated_data["library"]:
                raise ValidationError("Selected sequencings must belong to selected library")
        lanes = validated_data.pop('lanes')

        instance = DlpAnalysisInformation.objects.create(**validated_data)

        # Re-add many-to-many field
        instance.sequencings = sequencings
        instance.lanes = lanes
        instance.save()

        return instance

    def update(self, instance, validated_data):
        """Handle version field in here."""
        if 'version' in validated_data:
            validated_data['version'], _ = (
                DlpAnalysisVersion.objects.get_or_create(
                    version=validated_data['version']['version'],
                )
            )
        else:
            validated_data['version'] = instance.version

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
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


class JiraUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraUser
        fields = '__all__'



class TenxLaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxLane
        fields = '__all__'

class TenxSequencingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxSequencing
        fields = (
            'id',
            'tenx_pool',
            'sequencing_instrument',
            'submission_date',
            'tenxlane_set',
            'sequencer_id',
            'sequencing_center',
            'sequencer_notes',
            'number_of_lanes_requested',
            'lane_requested_date',
            'sequencer_notes',
            'gsc_library_id',
        )


    def to_representation(self, instance):
        value = super(TenxSequencingSerializer, self).to_representation(instance)
        value["library"] = [instance.library.id] if instance.library else []
        return value

class TenxLibraryConstructionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxLibraryConstructionInformation
        fields = "__all__"

class TenxLibrarySampleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxLibrarySampleDetail
        fields = "__all__"

class TenxLibraryQuantificationAndStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxLibraryQuantificationAndStorage
        fields = "__all__"

class TenxPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxPool
        fields = (
            'id',
            'pool_name',
            'gsc_pool_name',
            'construction_location',
            'constructed_date',
            'libraries',
        )

    def to_representation(self, instance):
        value = super(TenxPoolSerializer, self).to_representation(instance)
        value["tenxsequencing_set"] = [s.pk for s in  instance.tenxsequencing_set.all()]
        return value


class TenxLibrarySerializer(serializers.ModelSerializer):
    tenxsequencing_set = TenxSequencingSerializer(many=True, read_only=True)
    tenxpool_set = TenxPoolSerializer(many=True)
    tenxlibraryconstructioninformation = TenxLibraryConstructionInformationSerializer()
    tenxlibrarysampledetail = TenxLibrarySampleDetailSerializer()
    tenxlibraryquantificationandstorage = TenxLibraryQuantificationAndStorageSerializer()
    sample = SampleSerializer()
    projects = TagSerializerField(many=True, read_only=True)
    class Meta:
        editable = False,
        model = TenxLibrary
        fields = (
            'id',
            'name',
            'tenxpool_set',
            'jira_ticket',
            'tenxanalysis_set',
            'chips',
            'chip_well',
            'num_sublibraries',
            'tenxsequencing_set',
            'tenxlibraryconstructioninformation',
            'tenxlibrarysampledetail',
            'tenxlibraryquantificationandstorage',
            'projects',
            'sample',
            'relates_to_dlp',
            'relates_to_tenx',
            'description',
            'result',
            'failed',
        )

class TenxChipSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="get_id")
    tenxlibrary_set = TenxLibrarySerializer(many=True, read_only=True)
    class Meta:
        model = TenxChip
        fields = (
            'id',
            'lab_name',
            'name',
            'tenxlibrary_set',
        )


#----------------------------
#============================
# KUDU API
#----------------------------
#----------------------------


#============================
# CORE
#----------------------------
class KuduSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = (
            'id',
            'sample_id',
            'sample_type',
            'cell_line_id',
            'xenograft_id',
            'anonymous_patient_id',
        )


class KuduProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id',
            'name',
        )


#============================
# DLP
#----------------------------
class KuduDLPLibraryListSerializer(serializers.ModelSerializer):
    projects = KuduProjectSerializer(many=True, read_only=True)
    class Meta:
        model = DlpLibrary
        fields = (
            'id',
            'pool_id',
            'sample_id',
            'jira_ticket',
            'num_sublibraries',
            'projects',
        )

    def to_representation(self, instance):
        value = super(KuduDLPLibraryListSerializer, self).to_representation(instance)
        value['sample_id'] = get_object_or_404(Sample,id=value['sample_id']).sample_id
        value['projects'] = ", ".join([i["name"] for i in value['projects']])
        return value

class KuduDLPSublibrariesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SublibraryInformation
        fields = (
            "sample",
            "row",
            "column",
            "img_col",
            "file_ch1",
            "file_ch2",
            "fld_section",
            "fld_index",
            "num_live",
            "num_dead",
            "num_other",
            "rev_live",
            "rev_dead",
            "rev_other",
            "condition",
            "index_i7",
            "primer_i7",
            "index_i5",
            "primer_i5",
            "pick_met",
            "spot_well",
            "num_drops",
            "library",
            "chip_region",
        )

class KuduDLPLaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpLane
        fields = (
            'id',
            'flow_cell_id',
            'path_to_archive',
            'sequencing_date',
        )


class KuduDLPSequencingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpSequencing
        fields = (
            'id',
            'library',
            'gsc_library_id',
            'submission_date'
        )

    def to_representation(self, instance):
        value = super(KuduDLPSequencingSerializer, self).to_representation(instance)
        temp_lib = get_object_or_404(DlpLibrary,id=value['library'])
        value['jira_ticket'] = temp_lib.jira_ticket
        value['sample_id'] = get_object_or_404(Sample,id=temp_lib.sample_id).sample_id
        value['library'] = temp_lib.pool_id
        return value

class KuduDLPAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpAnalysisInformation
        fields = (
            'id',
            'analysis_run',
            'analysis_jira_ticket',
            'priority_level',
        )
    def to_representation(self, instance):
        value = super(KuduDLPAnalysisSerializer, self).to_representation(instance)
        temp_analysis = get_object_or_404(AnalysisRun,id=value['analysis_run'])
        value['last_updated'] = temp_analysis.last_updated
        value['run_status'] = temp_analysis.run_status
        return value

#============================
# TENX
#----------------------------

class KuduTenxLibraryListSerializer(serializers.ModelSerializer):
    projects = KuduProjectSerializer(many=True, read_only=True)
    class Meta:
        model = TenxLibrary
        fields = (
            'id',
            'name',
            'sample_id',
            'num_sublibraries',
            'projects',
        )
    def to_representation(self, instance):
        value = super(KuduTenxLibraryListSerializer, self).to_representation(instance)
        value['sample_id'] = get_object_or_404(Sample,id=value['sample_id']).sample_id
        value['projects'] = ", ".join([i["name"] for i in value['projects']])
        return value


class KuduTenxLaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxLane
        fields = (
            'id',
            'flow_cell_id',
            'path_to_archive',
            'sequencing_date',
        )


class KuduTenxPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxPool
        fields = (
            'id',
            'pool_name',
            'gsc_pool_name',
            'construction_location',
            'constructed_date'
        )


class KuduTenxChipSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="get_id")
    class Meta:
        model = TenxChip
        fields = (
            'id',
            'lab_name',
            'name'
        )

class KuduTenxSequencingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxSequencing
        fields = (
            'id',
            'tenx_pool',
            'sequencing_instrument',
            'submission_date',
            'sequencing_center',
            'number_of_lanes_requested',
            'lane_requested_date',
        )

class KuduTenxAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxAnalysis
        fields = (
            'id',
            'input_type',
            'jira_ticket',
            'version',
            'run_status'
        )