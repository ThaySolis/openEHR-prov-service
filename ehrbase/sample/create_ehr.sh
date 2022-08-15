#!/usr/bin/env bash

# Paths to useful directories.
SCRIPT_FOLDER=$( dirname -- "$( readlink -f -- "$0"; )"; )
SOURCE_FOLDER=$SCRIPT_FOLDER/../..

# Load variables from the .env file.
# source: https://gist.github.com/mihow/9c7f559807069a03e302605691f85572?permalink_comment_id=3770590#gistcomment-3770590
export $(echo $(cat "$SOURCE_FOLDER/.env" | sed 's/#.*//g'| xargs) | envsubst)

curl -k -v \
    -X PUT "$PRIVATE_OPENEHR_API_BASE_URI/v1/ehr/22222222-2222-2222-2222-222222222222" \
    -u "$OPENEHR_API_AUTH_USERNAME:$OPENEHR_API_AUTH_PASSWORD" \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "_type": "EHR_STATUS",
        "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
        "name": {
            "value": "EHR Status"
        },
        "subject": {},
        "is_modifiable": true,
        "is_queryable": true
    }'