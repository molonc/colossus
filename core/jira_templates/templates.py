# -*- coding: utf-8 -*-
"""Contains some templates of Jira descriptions."""

from core.models import Sample


# Provided by Emma Laks on 2018-08-17 and modified *just a touch* by
# Matt Wiens on 2018-08-18
DLP_UNFORMATTED_TEMPLATE = """Query the [Single Cell Database|http://colossus.bcgsc.ca] for detailed information.

Please check off the task list below as you complete the data transfers, and *do not resolve the ticket* until you have completed these tasks.

(x) Reference genome: {reference_genome}

(x) Raw data is available on BRC server (must be transferred to our servers)

(x) Data transferred to our servers

(x) Path to results on Genesis:
{{noformat}}
/projects/sftp/shahlab/singlecell/<jira_ticket_number>/
{{noformat}}

(x) Path to results in blob:

(x) Upload to Montage


---------



Query the [Single Cell Database|http://colossus.bcgsc.ca] for detailed information.

Please check off the task list below as you complete the data transfers, and *do not resolve the ticket* until you have completed these tasks.

(x) Reference genome: {reference_genome}

(x) Raw data is available on GSC server

(x) Path to results on Genesis:
{{noformat}}
/projects/sftp/shahlab/singlecell/<jira_ticket_number>/
{{noformat}}

(x) Path to results in blob:

(x) Upload to Montage
"""

# Provided by Ciara O'Flanagan on 2018-08-17
TENX_UNFORMATTED_TEMPLATE = """￼ Upload the web_summary.html file to the ticket 

Reference: {reference_genome}
Pool: {pool}

￼(x) Temp path to raw data on GSC server (must be transferred to our servers):
/home/aldente/private/Projects/Sam_Aparicio/

￼ (x) Temp path to Cellranger results (must be transferred to our servers):
/home/aldente/private/Projects/Sam_Aparicio/

￼ (x) Temp path to Sample Sheet:
/home/aldente/private/Projects/Sam_Aparicio/

(x)￼ Path to raw data on our server (must be backed up):
/shahlab/archive/single_cell_indexing/TENX/
"""


def get_reference_genome_from_sample_id(sample_id):
    """Get a reference genome given a Colossus sample ID.

    Arg:
        sample_id: A string containing a sample_id that exists in
            Colossus. For example, "DAH227A".
    Returns:
        A string containing the reference genome, which is either "hg19"
        or "mm10".
    """
    # Dictionary to get from "Taxonomy ID" to reference genome
    TAXONOMY_TO_REF_GENOME = {
        '9606': 'hg19',
        '10090': 'mm10'}

    # Get the "Taxonomy ID"
    taxonomy_id = Sample.objects.get(sample_id=sample_id).taxonomy_id

    return TAXONOMY_TO_REF_GENOME[taxonomy_id]


def generate_dlp_jira_description(reference_genome):
    """Generate a DLP Jira description.

    Arg:
        reference_genome: A string containing the reference genome.
            Should be either hg19 or mm10.
    Returns:
        A string containing the formatted Jira description.
    """
    return DLP_UNFORMATTED_TEMPLATE.format(reference_genome=reference_genome)

def generate_tenx_jira_description(reference_genome, pool):
    """Generate a Tenx Jira description.

    Args:
        reference_genome: A string containing the reference genome.
            Should be either hg19 or mm10.
        pool: A string containing the pool ID.
    Returns:
        A string containing the formatted Jira description.
    """
    return TENX_UNFORMATTED_TEMPLATE.format(
        reference_genome=reference_genome,
        pool=pool,
    )
