#!/usr/bin/env bash

SCRIPT_FOLDER=$( dirname -- "$( readlink -f -- "$0"; )"; )

SOURCE_FOLDER=$SCRIPT_FOLDER/../..

docker run -it --rm \
    --name "openehr-prov-service" \
    --env-file "$SOURCE_FOLDER/.env" \
    --network host \
    "openehr-prov-service-plain"
