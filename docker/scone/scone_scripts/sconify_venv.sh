#!/usr/bin/env bash

# This script runs inside SCONE.
# The following mounted directories are expected:
# - /venv -> The folder that will contain the virtual environment.
# - /scone_scripts -> The folder that contains this script.

# Paths to useful directories.
SCRIPT_FOLDER=$( dirname -- "$( readlink -f -- "$0"; )"; )
VENV_FOLDER=/venv
cd "$SCRIPT_FOLDER"

# Clears the virtual environment folder /bin folder.
rm -rf "$VENV_FOLDER/bin"

# Creates the folder with the SCONE-enabled Python executable.
mkdir -p "$VENV_FOLDER/bin"
cp -p "/usr/bin/python3" "$VENV_FOLDER/bin"
