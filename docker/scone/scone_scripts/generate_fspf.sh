#!/usr/bin/env bash

# This script runs inside SCONE.
# The following mounted directories are expected:
# - /app_original -> The folder that contains the original application.
# - /app -> The folder that will contain the encrypted application.
# - /fspf -> The folder that will contain the FSPF and related resources.
#   - .../fspf.pb
#   - .../keytag.out
# - /scone_scripts -> The folder that contains this script.

# Paths to useful directories.
SCRIPT_FOLDER=$( dirname -- "$( readlink -f -- "$0"; )"; )
APP_ORIGINAL_FOLDER=/app_original
APP_ENCRYPTED_FOLDER=/app
VENV_FOLDER=/venv
FSPF_FOLDER=/fspf
cd "$SCRIPT_FOLDER"

# Clear all content from the APP_ENCRYPTED and FSPF folders.
cd "$APP_ENCRYPTED_FOLDER"
rm -rf ./*
cd "$FSPF_FOLDER"
rm -rf ./*
cd "$SCRIPT_FOLDER"

# Create a FSPF file.
scone fspf create "$FSPF_FOLDER/fspf.pb"

# Mark the file system as a whole as non-protected.
scone fspf addr "$FSPF_FOLDER/fspf.pb" / --kernel / --not-protected

# Mark the VENV_FOLDER folder as authenticated.
scone fspf addr "$FSPF_FOLDER/fspf.pb" "$VENV_FOLDER" --kernel "$VENV_FOLDER" --authenticated
scone fspf addf "$FSPF_FOLDER/fspf.pb" "$VENV_FOLDER" "$VENV_FOLDER" "$VENV_FOLDER"

# Mark the APP_ENCRYPTED folder as encrypted.
scone fspf addr "$FSPF_FOLDER/fspf.pb" "$APP_ENCRYPTED_FOLDER" --kernel "$APP_ENCRYPTED_FOLDER" --encrypted

# Move all files from the APP_ORIGINAL folder to the APP_ENCRYPTED folder.
scone fspf addf "$FSPF_FOLDER/fspf.pb" "$APP_ENCRYPTED_FOLDER" "$APP_ORIGINAL_FOLDER" "$APP_ENCRYPTED_FOLDER"

# Encrypt the FSPF and store its key and tag to a file named 'keytag.out'.
scone fspf encrypt "$FSPF_FOLDER/fspf.pb" > "$FSPF_FOLDER/keytag.out"
