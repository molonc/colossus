# -*- coding: utf-8 -*-
"""Contains some templates of Jira descriptions."""

from core.models import Sample


# Provided by Emma Laks on 2018-08-17 and modified *just a touch* by
# Matt Wiens on 2018-08-18
# Completely gutted by Mike Yue 2019-02-14 due to request by Justina (Steps are now obsolete)
DLP_UNFORMATTED_TEMPLATE = """{description}

Query [Colossus|http://colossus.bcgsc.ca/dlp/library/{id}] for detailed information.

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


def generate_dlp_jira_description(library_description, library_id):
    """Generate a DLP Jira description.

    Arg:
        reference_genome: A string containing the reference genome.
            Should be either hg19 or mm10.
    Returns:
        A string containing the formatted Jira description.
    """
    return DLP_UNFORMATTED_TEMPLATE.format(description=library_description, id=library_id)

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
