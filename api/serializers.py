"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""

#============================
# Django rest framework imports
#----------------------------
import re

from rest_framework import serializers

#============================
# App imports
#----------------------------
from rest_framework.exceptions import ValidationError

from core.models import (
    DlpLibrary,
    Sample,
    AdditionalSampleInformation,
    SublibraryInformation,
    DlpSequencing,
    DlpLane,
    ChipRegionMetadata,
    MetadataField,
    ChipRegion,
    DlpLibraryConstructionInformation,
    DlpLibrarySampleDetail,
    JiraUser,
    Project,
    Analysis,
)

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
            'anonymous_patient_id',
            'cell_line_id',
            'sample_id',
            'sample_type',
            'taxonomy_id',
            'xenograft_id',
            'additionalsampleinformation',
        )


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = (
            'id',
            'input_type',
            'version',
            'jira_ticket',
            'run_status',
            'last_updated_date',
            'submission_date',
            'description',
            'dlp_library',
            'pbal_library',
            'tenx_library',
            'tenxsequencing_set',
            'dlpsequencing_set',
            'pbalsequencing_set'
        )

    def to_representation(self, instance):
        value = super(AnalysisSerializer, self).to_representation(instance)
        try:
            value["library"] =  value[value["input_type"].lower() + "_library"]
            del value["dlp_library"]
            del value["pbal_library"]
            del value["tenx_library"]
            #for now we only have tenx_sequencing
            value["sequencings"] = value[value["input_type"].lower() + 'sequencing_set']
            del value["dlpsequencing_set"]
            del value["pbalsequencing_set"]
            del value["tenxsequencing_set"]
            return value
        except:
            return value

    def create(self, validated_data):
        libraries = [validated_data["dlp_library"], validated_data["pbal_library"], validated_data["tenx_library"]]
        sequencings = [validated_data["dlpsequencing_set"], validated_data["pbalsequencing_set"], validated_data["tenxsequencing_set"]]
        if sum(1 for lib in libraries if lib) > 1:
            raise ValidationError("Only one Library Id must be provided")

        if sum(1 for lib in libraries if lib) == 0:
            raise ValidationError("Library must be set")

        if sum(1 for seq in sequencings if seq) > 1:
            raise ValidationError("Only " + validated_data["input_type"] + " Sequencing list must be provided")

        if sum(1 for seq in sequencings if seq) > 0 and not validated_data[validated_data["input_type"].lower() + 'sequencing_set']:
            raise ValidationError("Only " + validated_data["input_type"] + " Sequencing list must be provided")

        if not validated_data[validated_data["input_type"].lower() + "_library"]:
            raise ValidationError(
                "You specified input type to be " + validated_data["input_type"] + ", please provide the corresponding library id")

        if not re.match(r"(v\d+\.\d+\.\d+)", validated_data["version"]):
            raise ValidationError("Version must be in the format of v\d+\.\d+\.\d+")

        return super(AnalysisSerializer, self).create(validated_data)

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
    dlplane_set = LaneSerializer(many=True, read_only=True)
    class Meta:
        model = DlpSequencing
        fields = (
            'id',
            'library',
            'adapter',
            'read_type',
            'index_read_type',
            'sequencing_instrument',
            'submission_date',
            'dlplane_set',
            'gsc_library_id',
            'sequencing_center',
            'rev_comp_override',
            'number_of_lanes_requested',
        )


class TagSerializerField(serializers.ListField):
    child = serializers.CharField()

    def to_representation(self, data):
        return data.values_list('name', flat=True)


class DlpLibraryConstructionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpLibraryConstructionInformation
        fields = '__all__'


class DlpLibrarySampleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlpLibrarySampleDetail
        fields = '__all__'


class LibrarySerializer(serializers.ModelSerializer):
    sample = SampleSerializer()
    dlplibraryconstructioninformation = DlpLibraryConstructionInformationSerializer()
    dlplibrarysampledetail = DlpLibrarySampleDetailSerializer()
    dlpsequencing_set = SequencingSerializer(many=True, read_only=True)
    projects = TagSerializerField()
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
            'exclude_from_analysis',
        )

    def validate(self, data):
        data["sample"] = data["sample"]["sample_id"]
        data["relates_to_dlp"] = [p.id for p in data["relates_to_dlp"]]
        data["relates_to_tenx"] = [p.id for p in data["relates_to_tenx"]]
        data["sample"] = Sample.objects.filter(sample_id=data["sample"])[0]
        data["projects"] = [p.id for p in Project.objects.filter(name__in=data["projects"])]

        return data

    def create(self, validated_data):
        construction_info = validated_data["dlplibraryconstructioninformation"]
        relates_to_dlp = validated_data["relates_to_dlp"]
        relates_to_tenx = validated_data["relates_to_tenx"]
        projects = validated_data["projects"]

        del validated_data["dlplibraryconstructioninformation"]
        del validated_data["relates_to_dlp"]
        del validated_data["relates_to_tenx"]
        del validated_data["projects"]

        instance = DlpLibrary.objects.create(**validated_data)
        instance.save()
        info = DlpLibraryConstructionInformation.objects.create(**construction_info)
        info.save()
        instance.dlplibraryconstructioninformation = info

        instance.projects.add(*projects)
        instance.relates_to_dlp.add(*relates_to_dlp)
        instance.relates_to_tenx.add(*relates_to_tenx)

        return instance

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
        instance = DlpAnalysisInformation.objects.create(**validated_data)
        instance.full_clean()
        instance.save()

        # Re-add many to many field
        instance.sequencings = sequencings
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

        instance = DlpAnalysisInformation.objects.create(**validated_data)

        # Re-add many-to-many field
        instance.sequencings = sequencings
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
    tenxlane_set = TenxLaneSerializer(many=True, read_only=True)
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
        )


    def to_representation(self, instance):
        value = super(TenxSequencingSerializer, self).to_representation(instance)
        value["library"] = [instance.library.id] if instance.library else []
        return value

class TenxLibraryConstructionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenxLibraryConstructionInformation
        fields = "__all__"


class TenxLibrarySerializer(serializers.ModelSerializer):
    tenxsequencing_set = TenxSequencingSerializer(many=True, read_only=True)
    tenxlibraryconstructioninformation = TenxLibraryConstructionInformationSerializer(read_only=True)
    sample = SampleSerializer()
    projects = TagSerializerField()
    class Meta:
        editable = False,
        model = TenxLibrary
        fields = (
            'id',
            'name',
            'jira_ticket',
            'chips',
            'chip_well',
            'condition',
            'num_sublibraries',
            'tenxsequencing_set',
            'tenxlibraryconstructioninformation',
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
