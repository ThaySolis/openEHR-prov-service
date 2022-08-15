#!/usr/bin/env bash

# This script runs outside SCONE.
# The following mounted directories are expected:
# - /venv -> The folder that will contain the virtual environment.
# - /app_original -> The folder that contains the original application.
# - /scone_scripts -> The folder that contains this script.

# Paths to useful directories.
SCRIPT_FOLDER=$( dirname -- "$( readlink -f -- "$0"; )"; )
APP_ORIGINAL_FOLDER=/app_original
VENV_FOLDER=/venv
cd "$SCRIPT_FOLDER"

# Clears the virtual environment folder.
cd "$VENV_FOLDER"
rm -rf ./*
cd "$SCRIPT_FOLDER"

# Generates a new virtual environment.
python3 -m venv "$VENV_FOLDER"

# Installs all dependencies on the virtual environment.
"$VENV_FOLDER/bin/python3" -m pip install -r "$APP_ORIGINAL_FOLDER/requirements.txt"

# Remove LXML dependency from PROV.
# This is hacky. We overwrite the PROV XML serializer with our own.

cat "$SCRIPT_FOLDER/provxml_replacement_serializer.py" > "$VENV_FOLDER/lib/python3.7/site-packages/prov/serializers/provxml.py"
cat "$SCRIPT_FOLDER/provxml_replacement_serializer.py" > "$VENV_FOLDER/lib64/python3.7/site-packages/prov/serializers/provxml.py"
