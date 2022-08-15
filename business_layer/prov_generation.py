from prov.model import ProvDocument

from data_layer import openehr_api, demographic_api, rm_utils

def create_prov_document_of_ehr_status(ehr_id):
    """
    Creates the PROV document of the EHR Status of a given EHR.

    Parameters:
        ehr_id - the ID of the EHR.

    Returns:
        The provenance document.
    """

    # creates the provenance document
    doc = ProvDocument()

    # PROV uses namespaces like XML.
    # All used namespaces must be declared explicitly, except the standard ones.
    doc.add_namespace("openehr", "http://schemas.openehr.org/v2")

    agents = set()
    version_ids = openehr_api.get_version_ids_of_ehr_status(ehr_id)
    for i in range(0, len(version_ids)):
        version_id = version_ids[i]

        version = openehr_api.get_versioned_ehr_status_version_by_id(ehr_id, version_id)
        contribution_id = rm_utils.extract_contribution_id_from_version(version)
        committer_name_or_id = rm_utils.extract_committer_name_or_id_from_version(version)

        doc.entity(f"openehr:{version_id}", other_attributes = {"prov:type": "openehr:EHR_STATUS"})
        doc.activity(f"openehr:{contribution_id}", other_attributes = {"prov:type": "openehr:CONTRIBUTION"})
        doc.wasGeneratedBy(entity = f"openehr:{version_id}", activity = f"openehr:{contribution_id}")

        if committer_name_or_id is not None:
            if committer_name_or_id not in agents:
                agents.add(committer_name_or_id)
                doc.agent(f"openehr:committer_{committer_name_or_id}", other_attributes = {"prov:type": "openehr:PARTY_IDENTIFIED"})

            doc.wasAttributedTo(entity = f"openehr:{version_id}", agent = f"openehr:committer_{committer_name_or_id}")
            doc.wasAssociatedWith(activity = f"openehr:{contribution_id}", agent = f"openehr:committer_{committer_name_or_id}")

        if i > 0:
            previous_version_id = version_ids[i - 1]
            doc.wasDerivedFrom(f"openehr:{version_id}", f"openehr:{previous_version_id}")
            doc.used(f"openehr:{contribution_id}", f"openehr:{previous_version_id}")

    return doc

def create_prov_document_of_composition(ehr_id, composition_id):
    """
    Creates the PROV document of a COMPOSITION of a given EHR.

    Parameters:
        ehr_id - the ID of the EHR.
        composition_id - the ID of the COMPOSITION.

    Returns:
        The provenance document.
    """

    # creates the provenance document
    doc = ProvDocument()

    # PROV uses namespaces like XML.
    # All used namespaces must be declared explicitly, except the standard ones.
    doc.add_namespace("openehr", "http://schemas.openehr.org/v2")

    agents = set()
    version_ids = openehr_api.get_version_ids_of_composition(ehr_id, composition_id)
    for i in range(0, len(version_ids)):
        version_id = version_ids[i]

        version = openehr_api.get_versioned_composition_version_by_id(ehr_id, composition_id, version_id)
        contribution_id = rm_utils.extract_contribution_id_from_version(version)
        committer_name_or_id = rm_utils.extract_committer_name_or_id_from_version(version)

        doc.entity(f"openehr:{version_id}", other_attributes = {"prov:type": "openehr:COMPOSITION"})
        doc.activity(f"openehr:{contribution_id}", other_attributes = {"prov:type": "openehr:CONTRIBUTION"})
        doc.wasGeneratedBy(entity = f"openehr:{version_id}", activity = f"openehr:{contribution_id}")

        if committer_name_or_id is not None:
            if committer_name_or_id not in agents:
                agents.add(committer_name_or_id)
                doc.agent(f"openehr:committer_{committer_name_or_id}", other_attributes = {"prov:type": "openehr:PARTY_IDENTIFIED"})

            doc.wasAttributedTo(entity = f"openehr:{version_id}", agent = f"openehr:committer_{committer_name_or_id}")
            doc.wasAssociatedWith(activity = f"openehr:{contribution_id}", agent = f"openehr:committer_{committer_name_or_id}")

        if i > 0:
            previous_version_id = version_ids[i - 1]
            doc.wasDerivedFrom(f"openehr:{version_id}", f"openehr:{previous_version_id}")
            doc.used(f"openehr:{contribution_id}", f"openehr:{previous_version_id}")

    return doc

def create_prov_document_of_patient(patient_id):
    """
    Creates the PROV document of the given patient.

    Parameters:
        patient_id - the ID of the patient.

    Returns:
        The provenance document.
    """

    # creates the provenance document
    doc = ProvDocument()

    # PROV uses namespaces like XML.
    # All used namespaces must be declared explicitly, except the standard ones.
    doc.add_namespace("openehr", "http://schemas.openehr.org/v2")

    agents = set()
    version_ids = demographic_api.get_version_ids_of_patient(patient_id)
    for i in range(0, len(version_ids)):
        version_id = version_ids[i]

        version = demographic_api.get_versioned_patient_version_by_id(patient_id, version_id)
        contribution_id = rm_utils.extract_contribution_id_from_version(version)
        committer_name_or_id = rm_utils.extract_committer_name_or_id_from_version(version)

        doc.entity(f"openehr:{version_id}", other_attributes = {"prov:type": "openehr:PERSON"})
        doc.activity(f"openehr:{contribution_id}", other_attributes = {"prov:type": "openehr:CONTRIBUTION"})
        doc.wasGeneratedBy(entity = f"openehr:{version_id}", activity = f"openehr:{contribution_id}")

        if committer_name_or_id is not None:
            if committer_name_or_id not in agents:
                agents.add(committer_name_or_id)
                doc.agent(f"openehr:committer_{committer_name_or_id}", other_attributes = {"prov:type": "openehr:PARTY_IDENTIFIED"})

            doc.wasAttributedTo(entity = f"openehr:{version_id}", agent = f"openehr:committer_{committer_name_or_id}")
            doc.wasAssociatedWith(activity = f"openehr:{contribution_id}", agent = f"openehr:committer_{committer_name_or_id}")

        if i > 0:
            previous_version_id = version_ids[i - 1]
            doc.wasDerivedFrom(f"openehr:{version_id}", f"openehr:{previous_version_id}")
            doc.used(f"openehr:{contribution_id}", f"openehr:{previous_version_id}")

    return doc
