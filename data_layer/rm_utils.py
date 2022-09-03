def extract_contribution_id_from_version(version : dict) -> str:
    # the VERSION<T> has the following format:
    # {
    #   "contribution": {
    #     "uid": {
    #       "value": <contribution_id>
    #     },
    #     ...
    #   },
    #   ...
    # }
    # documentation: https://specifications.openehr.org/releases/RM/latest/common.html#_version_class

    contribution_object_ref = version["contribution"]
    if "uid" in contribution_object_ref:
        contribution_id = contribution_object_ref["uid"]["value"]
    else:
        # fallback from wrongly-formatted OBJECT_REF
        contribution_id = contribution_object_ref["id"]["value"]

    return contribution_id

def extract_committer_name_or_id_from_version(version : dict) -> dict:
    # the VERSION<T> has the following format:
    # {
    #   "commit_audit": {
    #     "committer": {
    #       "_type": "PARTY_IDENTIFIED",
    #       "name": <name>,
    #       "identifiers": [
    #         {
    #           "id": <id>,
    #           ...
    #         },
    #         ...
    #       ]
    #     },
    #     ...
    #   }
    #   ...
    # }
    # documentation: https://specifications.openehr.org/releases/RM/latest/common.html#_version_class
    # documentation: https://specifications.openehr.org/releases/RM/latest/common.html#_audit_details_class
    # documentation: https://specifications.openehr.org/releases/RM/latest/common.html#_party_identified_class
    # documentation: https://specifications.openehr.org/releases/RM/latest/data_types.html#_dv_identifier_class

    committer_name_or_id = None

    audit_details = version["commit_audit"]
    committer = audit_details["committer"]
    if "_type" in committer and committer["_type"] == "PARTY_IDENTIFIED":
        if "name" in committer:
            committer_name_or_id = committer["name"]
        else:
            committer_name_or_id = committer["identifiers"][0]["id"]

    return committer_name_or_id
