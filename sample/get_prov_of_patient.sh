#!/usr/bin/env bash

# Paths to useful directories.
SCRIPT_FOLDER=$( dirname -- "$( readlink -f -- "$0"; )"; )
SOURCE_FOLDER=$SCRIPT_FOLDER/..

# Load variables from the .env file.
# source: https://gist.github.com/mihow/9c7f559807069a03e302605691f85572?permalink_comment_id=3770590#gistcomment-3770590
export $(echo $(cat "$SOURCE_FOLDER/.env" | sed 's/#.*//g'| xargs) | envsubst)

# Guess protocol based on environment variables.
HTTP_OR_HTTPS=https
if [ $PLAIN_HTTP == "yes" ]
then
    HTTP_OR_HTTPS=http
fi

# Send request.
curl -k -v \
    -X GET "$HTTP_OR_HTTPS://127.0.0.1:$SERVER_PORT/provenance/service?target=$PUBLIC_DEMOGRAPHIC_API_BASE_URI/v1/patient/11111111-1111-1111-1111-111111111111" \
    -u "$AUTH_USERNAME:$AUTH_PASSWORD"
