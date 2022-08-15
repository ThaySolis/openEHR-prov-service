#!/usr/bin/env bash

# Determines the SGX device.
# Adapted from <https://sconedocs.github.io/sgxinstall/#determine-sgx-device>
export SGXDEVICE="/dev/sgx/enclave"
export MOUNT_SGXDEVICE="--device=/dev/sgx/enclave --device=/dev/sgx/provision"
export SCONE_MODE="hw"
if [[ ! -e "$SGXDEVICE" ]] ; then
    export SGXDEVICE="/dev/sgx"
    export MOUNT_SGXDEVICE="--device=/dev/sgx"
    if [[ ! -e "$SGXDEVICE" ]] ; then
        export SGXDEVICE="/dev/isgx"
        export MOUNT_SGXDEVICE="--device=/dev/isgx"
        if [[ ! -c "$SGXDEVICE" ]] ; then
            echo "Warning: No SGX device found! Will run in SIM mode." > /dev/stderr
            export MOUNT_SGXDEVICE=""
            export SGXDEVICE=""
            export SCONE_MODE="sim"
        fi
    fi
fi
# LAS/CAS configuration.
LAS_ADDR=$( hostname -I | cut -d' ' -f1 )
CAS_ADDR=5-7-0.scone-cas.cf

# Paths to useful directories.
SCRIPT_FOLDER=$( dirname -- "$( readlink -f -- "$0"; )"; )
RESOURCES_FOLDER=$SCRIPT_FOLDER/_resources
CAS_SESSION_FOLDER=$RESOURCES_FOLDER/cas_session

# Get the configuration ID from the CAS session.
CAS_CONFIG_ID=$(cat "$CAS_SESSION_FOLDER/cas-config-id.out")

# Run the container
docker run -it --rm \
    --name "openehr-prov-service" \
    $MOUNT_SGXDEVICE \
    -e "SCONE_MODE=$SCONE_MODE" \
    -e "SCONE_LAS_ADDR=$LAS_ADDR" \
    -e "SCONE_CAS_ADDR=$CAS_ADDR" \
    -e "SCONE_CONFIG_ID=$CAS_CONFIG_ID/api_service" \
    --network host \
    "openehr-prov-service-scone"
