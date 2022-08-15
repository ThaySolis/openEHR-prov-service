#!/usr/bin/env bash

# Paths to useful directories.
SCRIPT_FOLDER=$( dirname -- "$( readlink -f -- "$0"; )"; )
SOURCE_FOLDER=$SCRIPT_FOLDER/../..

# Load variables from the .env file.
# source: https://gist.github.com/mihow/9c7f559807069a03e302605691f85572?permalink_comment_id=3770590#gistcomment-3770590
export $(echo $(cat "$SOURCE_FOLDER/.env" | sed 's/#.*//g'| xargs) | envsubst)

curl -k -v \
    -X POST "$PRIVATE_OPENEHR_API_BASE_URI/v1/ehr/22222222-2222-2222-2222-222222222222/composition" \
    -u "$OPENEHR_API_AUTH_USERNAME:$OPENEHR_API_AUTH_PASSWORD" \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "_type": "COMPOSITION",
        "name": {
            "_type": "DV_TEXT",
            "value": "Bericht"
        },
        "archetype_details": {
            "archetype_id": {
                "value": "openEHR-EHR-COMPOSITION.report.v1"
            },
            "template_id": {
                "value": "Corona_Anamnese"
            },
            "rm_version": "1.0.4"
        },
        "language": {
            "_type": "CODE_PHRASE",
            "terminology_id": {
                "_type": "TERMINOLOGY_ID",
                "value": "ISO_639-1"
            },
            "code_string": "de"
        },
        "territory": {
            "_type": "CODE_PHRASE",
            "terminology_id": {
                "_type": "TERMINOLOGY_ID",
                "value": "ISO_3166-1"
            },
            "code_string": "GE"
        },
        "category": {
            "_type": "DV_CODED_TEXT",
            "value": "event",
            "defining_code": {
                "_type": "CODE_PHRASE",
                "terminology_id": {
                    "_type": "TERMINOLOGY_ID",
                    "value": "openehr"
                },
                "code_string": "433"
            }
        },
        "composer": {
            "_type": "PARTY_IDENTIFIED",
            "name": "Wein"
        },
        "context": {
            "_type": "EVENT_CONTEXT",
            "start_time": {
                "_type": "DV_DATE_TIME",
                "value": "2021-08-24T22:26:32,682Z"
            },
            "setting": {
                "_type": "DV_CODED_TEXT",
                "value": "home",
                "defining_code": {
                    "_type": "CODE_PHRASE",
                    "terminology_id": {
                        "_type": "TERMINOLOGY_ID",
                        "value": "openehr"
                    },
                    "code_string": "225"
                }
            },
            "other_context": {
                "_type": "ITEM_TREE",
                "name": {
                    "_type": "DV_TEXT",
                    "value": "Tree"
                },
                "items": [
                    {
                        "_type": "ELEMENT",
                        "name": {
                            "_type": "DV_TEXT",
                            "value": "Bericht ID"
                        },
                        "value": {
                            "_type": "DV_TEXT",
                            "value": "Kartoffeln"
                        },
                        "archetype_node_id": "at0002"
                    }
                ],
                "archetype_node_id": "at0001"
            },
            "health_care_facility": {
                "_type": "PARTY_IDENTIFIED",
                "name": "Bier"
            }
        },
        "archetype_node_id": "openEHR-EHR-COMPOSITION.report.v1"
    }'