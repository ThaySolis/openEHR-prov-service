import prov.model

from data_layer import api_exceptions, classifier

from business_layer import prov_generation, controller_exceptions

def get_provenance(uri : str) -> prov.model.ProvDocument:
    classification = classifier.classify_uri(uri)
    if classification is None:
        raise controller_exceptions.InvalidURIException(f"Invalid URI: {uri}.")

    classification_type = classification["type"]
    if classification_type == "EHR_STATUS":
        ehr_id = classification["ehr_id"]
        return get_provenance_of_ehr_status(ehr_id)
    elif classification_type == "COMPOSITION":
        ehr_id = classification["ehr_id"]
        composition_id = classification["composition_id"]
        return get_provenance_of_composition(ehr_id, composition_id)
    elif classification_type == "patient":
        patient_id = classification["patient_id"]
        return get_provenance_of_patient(patient_id)

    raise controller_exceptions.InternalException(f"The URL class '{ classification_type }' is not supported!")

def get_provenance_of_ehr_status(ehr_id : str) -> prov.model.ProvDocument:
    try:
        return prov_generation.create_prov_document_of_ehr_status(ehr_id)
    except api_exceptions.NotFoundException:
        raise controller_exceptions.NoSuchVersionedObjectException(f"No such EHR {ehr_id}!")

def get_provenance_of_composition(ehr_id : str, composition_id : str) -> prov.model.ProvDocument:
    try:
        return prov_generation.create_prov_document_of_composition(ehr_id, composition_id)
    except api_exceptions.NotFoundException:
        raise controller_exceptions.NoSuchVersionedObjectException(f"No such composition {composition_id} or no such EHR {ehr_id}!")

def get_provenance_of_patient(patient_id : str) -> prov.model.ProvDocument:
    try:
        return prov_generation.create_prov_document_of_patient(patient_id)
    except api_exceptions.NotFoundException:
        raise controller_exceptions.NoSuchVersionedObjectException(f"No such patient {patient_id}!")
