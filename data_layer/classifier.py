from urllib.parse import urlparse
from pathlib import PurePosixPath

from app_settings import PUBLIC_OPENEHR_API_BASE_URI, PUBLIC_DEMOGRAPHIC_API_BASE_URI
from data_layer import ids

openehr_api_base_uri = PUBLIC_OPENEHR_API_BASE_URI
if openehr_api_base_uri[-1] != "/":
    openehr_api_base_uri += "/"
parsed_openehr_api_base_uri = urlparse(openehr_api_base_uri)

demographic_api_base_uri = PUBLIC_DEMOGRAPHIC_API_BASE_URI
if demographic_api_base_uri[-1] != "/":
    demographic_api_base_uri += "/"
parsed_demographic_api_base_uri = urlparse(demographic_api_base_uri)

def classify_uri(uri : str) -> dict:
    """
    Classifies a given URI in:
    - EHR_STATUS
    - COMPOSITION
    - Patient

    If the URI corresponds to an EHR_STATUS URI, this method returns a dictionary with the following format:
    ```json
    {
        "type": "EHR_STATUS",
        "ehr_id": <the EHR identifier>
    }
    ```

    If the URI corresponds to a COMPOSITION URI, this method returns a dictionary with the following format:
    ```json
    {
        "type": "COMPOSITION",
        "ehr_id": <the EHR identifier>,
        "composition_id": <the COMPOSITION identifier>
    }
    ```

    If the URI corresponds to a patient URI, this method returns a dictionary with the following format:
    ```json
    {
        "type": "patient",
        "patient_id": <the patient identifier>
    }
    ```

    If the URI does not correspond to a valid pattern, this function returns `None`.

    Arguments:
        - uri: A string with the URI to classify.

    Return:
        A dictionary or `None`,
    """

    #Tenta classificar como URI da API do OpenEHR
    result = classify_openehr_uri(uri)
    if result is not None:
        return result

    #Tenta classificar como URI da API demográfica
    result = classify_demographic_uri(uri)
    if result is not None:
        return result

    return None

def classify_openehr_uri(uri : str) -> dict:
    if not uri.startswith(openehr_api_base_uri):
        return None

    parsed_uri = urlparse(uri)
    path = parsed_uri.path[len(parsed_openehr_api_base_uri.path):]
    if len(path) == 0:
        return None

    parsed_path = PurePosixPath(path).parts

    if parsed_path[0] == "v1":
        if len(parsed_path) > 1:
            if parsed_path[1] == "ehr":
                if len(parsed_path) > 2:
                    ehr_id = parsed_path[2]

                    if len(parsed_path) > 3:
                        if parsed_path[3] == "ehr_status":
                            if len(parsed_path) == 4:
                                #{openehr_api_base_uri}/v1/ehr/<ehr_id>/ehr_status
                                return {
                                    "type": "EHR_STATUS",
                                    "ehr_id": ehr_id
                                }
                            else:
                                version_id = parsed_path[4]

                                if len(parsed_path) == 5:
                                    #{openehr_api_base_uri}/v1/ehr/<ehr_id>/ehr_status/<version_id>
                                    return {
                                        "type": "EHR_STATUS",
                                        "ehr_id": ehr_id
                                    }
                        if parsed_path[3] == "versioned_ehr_status":
                            if len(parsed_path) == 4:
                                #{openehr_api_base_uri}/v1/ehr/<ehr_id>/versioned_ehr_status
                                return {
                                    "type": "EHR_STATUS",
                                    "ehr_id": ehr_id
                                }
                            else:
                                if parsed_path[4] == "version":
                                    if len(parsed_path) == 5:
                                        #{openehr_api_base_uri}/v1/ehr/<ehr_id>/versioned_ehr_status/version
                                        return {
                                            "type": "EHR_STATUS",
                                            "ehr_id": ehr_id
                                        }
                                    else:
                                        version_id = parsed_path[5]

                                        if len(parsed_path) == 6:
                                            #{openehr_api_base_uri}/v1/ehr/<ehr_id>/versioned_ehr_status/version/<version_id>
                                            return {
                                                "type": "EHR_STATUS",
                                                "ehr_id": ehr_id
                                            }
                        if parsed_path[3] == "composition":
                            if len(parsed_path) > 4:
                                version_id_or_composition_id = parsed_path[4]
                                if ids.is_version_id(version_id_or_composition_id):
                                    version_id = version_id_or_composition_id
                                    composition_id = ids.extract_versioned_object_id_from_version_id(version_id)
                                else:
                                    composition_id = version_id_or_composition_id

                                if len(parsed_path) == 5:
                                    # {openehr_api_base_uri}/ehr/<ehr_id>/composition/<version_id_or_composition_id>
                                    return {
                                        "type": "COMPOSITION",
                                        "ehr_id": ehr_id,
                                        "composition_id": composition_id
                                    }
                        if parsed_path[3] == "versioned_composition":
                            if len(parsed_path) > 4:
                                composition_id = parsed_path[4]

                                if len(parsed_path) == 5:
                                    #{openehr_api_base_uri}/v1/ehr/<ehr_id>/versioned_composition/<composition_id>
                                    return {
                                        "type": "COMPOSITION",
                                        "ehr_id": ehr_id,
                                        "composition_id": composition_id
                                    }
                                else:
                                    if len(parsed_path) == 6:
                                        #{openehr_api_base_uri}/v1/ehr/<ehr_id>/versioned_composition/<composition_id>/version
                                        return {
                                            "type": "COMPOSITION",
                                            "ehr_id": ehr_id,
                                            "composition_id": composition_id
                                        }
                                    else:
                                        if len(parsed_path) == 7:
                                            version_id = parsed_path[6]

                                            #{openehr_api_base_uri}/v1/ehr/<ehr_id>/versioned_composition/<composition_id>/version/<version_id>
                                            return {
                                                "type": "COMPOSITION",
                                                "ehr_id": ehr_id,
                                                "composition_id": composition_id
                                            }

    return None

def classify_demographic_uri(uri : str) -> dict:
    if not uri.startswith(demographic_api_base_uri):
        return None

    parsed_uri = urlparse(uri)
    path = parsed_uri.path[len(parsed_demographic_api_base_uri.path):]
    if len(path) == 0:
        return None

    parsed_path = PurePosixPath(path).parts

    if parsed_path[0] == "v1":
        if len(parsed_path) > 1:
            if parsed_path[1] == "patient":
                if len(parsed_path) > 2:
                    version_id_or_patient_id = parsed_path[2]
                    if ids.is_version_id(version_id_or_patient_id):
                        version_id = version_id_or_patient_id
                        patient_id = ids.extract_versioned_object_id_from_version_id(version_id)
                    else:
                        patient_id = version_id_or_patient_id

                    if len(parsed_path) == 3:
                        #{parsed_demographic_api_base_uri}/v1/patient/<version_id_or_patient_id>
                        return {
                            "type": "patient",
                            "patient_id": patient_id
                        }
            elif parsed_path[1] == "versioned_patient":
                if len(parsed_path) > 2:
                    patient_id = parsed_path[2]

                    if len(parsed_path) == 3:
                        #{parsed_demographic_api_base_uri}/v1/versioned_patient/<patient_id>
                        return {
                            "type": "patient",
                            "patient_id": patient_id
                        }
                    else:
                        if len(parsed_path) == 4:
                            #{parsed_demographic_api_base_uri}/v1/versioned_patient/<patient_id>/version
                            return {
                                "type": "patient",
                                "patient_id": patient_id
                            }
                        else:
                            version_id = parsed_path[4]

                            if len(parsed_path) == 5:
                                #{parsed_demographic_api_base_uri}/v1/versioned_patient/<patient_id>/version/<version_id>
                                return {
                                    "type": "patient",
                                    "patient_id": patient_id
                                }

    return None
