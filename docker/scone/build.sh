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

# SCONE images
PYTHON_PLAIN_IMAGE=python:3.7.3
PYTHON_SCONE_IMAGE=registry.scontain.com:5050/sconecuratedimages/apps:python-3.7.3-alpine3.10-scone5.3.0
COMPILERS_SCONE_IMAGE=registry.scontain.com:5050/sconecuratedimages/crosscompilers

# CAS configuration.
CAS_ADDR=5-7-0.scone-cas.cf
CAS_MRENCLAVE="3061b9feb7fa67f3815336a085f629a13f04b0a1667c93b14ff35581dc8271e4"

# Paths to useful directories.
SCRIPT_FOLDER=$( dirname -- "$( readlink -f -- "$0"; )"; )
SOURCE_FOLDER=$SCRIPT_FOLDER/../..
RESOURCES_FOLDER=$SCRIPT_FOLDER/_resources
APP_ORIGINAL_FOLDER=$RESOURCES_FOLDER/app_original
APP_ENCRYPTED_FOLDER=$RESOURCES_FOLDER/app_encrypted
VENV_FOLDER=$RESOURCES_FOLDER/venv
FSPF_FOLDER=$RESOURCES_FOLDER/fspf
CAS_SESSION_FOLDER=$RESOURCES_FOLDER/cas_session
SCONE_SCRIPTS_FOLDER=$SCRIPT_FOLDER/scone_scripts

# Generate the data folder if it does not exist.
mkdir -p "$RESOURCES_FOLDER"

# Copy source files to the original app folder.
rm -rf "$APP_ORIGINAL_FOLDER"
mkdir -p "$APP_ORIGINAL_FOLDER"
mkdir -p "$APP_ORIGINAL_FOLDER/certificate/"
cp "$SOURCE_FOLDER/requirements.txt" "$APP_ORIGINAL_FOLDER/"
cp "$SOURCE_FOLDER/app.py" "$APP_ORIGINAL_FOLDER/"
cp "$SOURCE_FOLDER/app_settings.py" "$APP_ORIGINAL_FOLDER/"
cp "$SOURCE_FOLDER/authentication.py" "$APP_ORIGINAL_FOLDER/"
cp -r "$SOURCE_FOLDER/data_layer" "$APP_ORIGINAL_FOLDER/"
cp -r "$SOURCE_FOLDER/business_layer" "$APP_ORIGINAL_FOLDER/"
cp -r "$SOURCE_FOLDER/presentation_layer" "$APP_ORIGINAL_FOLDER/"
cp "$SOURCE_FOLDER/certificate/api-cert.pem" "$APP_ORIGINAL_FOLDER/certificate/"
cp "$SOURCE_FOLDER/certificate/api-key.pem" "$APP_ORIGINAL_FOLDER/certificate/"
cp -r "$SOURCE_FOLDER/other_certificates" "$APP_ORIGINAL_FOLDER/"

# Make sure the output folders exists.
mkdir -p "$APP_ENCRYPTED_FOLDER"
mkdir -p "$VENV_FOLDER"
mkdir -p "$FSPF_FOLDER"
mkdir -p "$CAS_SESSION_FOLDER"

# Run the container which generates the virtual environment.
docker run -it --rm \
    $MOUNT_SGXDEVICE -e "SCONE_MODE=$SCONE_MODE" \
    -v "$VENV_FOLDER/:/venv" \
    -v "$APP_ORIGINAL_FOLDER:/app_original" \
    -v "$SCONE_SCRIPTS_FOLDER/:/scone_scripts" \
    "$PYTHON_PLAIN_IMAGE" \
    "/scone_scripts/generate_venv.sh"

# Run the container which sconifies the virtual environment.
docker run -it --rm \
    $MOUNT_SGXDEVICE -e "SCONE_MODE=$SCONE_MODE" \
    -v "SCONE_FORK=1" \
    -v "$VENV_FOLDER/:/venv" \
    -v "$APP_ORIGINAL_FOLDER:/app_original" \
    -v "$SCONE_SCRIPTS_FOLDER/:/scone_scripts" \
    "$PYTHON_SCONE_IMAGE" \
    "/scone_scripts/sconify_venv.sh"

# Run the container which generates the FSPF and encrypts files.
docker run -it --rm \
    $MOUNT_SGXDEVICE -e "SCONE_MODE=$SCONE_MODE" \
    -v "$VENV_FOLDER:/venv" \
    -v "$APP_ORIGINAL_FOLDER:/app_original" \
    -v "$APP_ENCRYPTED_FOLDER:/app" \
    -v "$FSPF_FOLDER:/fspf" \
    -v "$SCONE_SCRIPTS_FOLDER/:/scone_scripts" \
    "$COMPILERS_SCONE_IMAGE" \
    "/scone_scripts/generate_fspf.sh"

# Extract the generated key and tag.
SCONE_FSPF_KEY=$(cat "$FSPF_FOLDER/keytag.out" | awk '{print $11}')
SCONE_FSPF_TAG=$(cat "$FSPF_FOLDER/keytag.out" | awk '{print $9}')

# Generates a certificate-key pair to authenticate with the CAS.
rm -f "$CAS_SESSION_FOLDER/cas-cert.pem"
rm -f "$CAS_SESSION_FOLDER/cas-key.pem"
openssl req -newkey rsa:4096 -days 365 -nodes -x509 \
    -out "$CAS_SESSION_FOLDER/cas-cert.pem" \
    -keyout "$CAS_SESSION_FOLDER/cas-key.pem" \
    -config "$SCRIPT_FOLDER/cas-certreq.conf"

# copy the session template to the CAS session folder.
cp -f "$SCRIPT_FOLDER/cas-session-template.yml" "$CAS_SESSION_FOLDER/"

# Run the container which generates the session with the CAS.
docker run -it --rm \
    $MOUNT_SGXDEVICE -e "SCONE_MODE=$SCONE_MODE" \
    --env-file "$SOURCE_FOLDER/.env" \
    -e "FSPF_KEY=$SCONE_FSPF_KEY" \
    -e "FSPF_TAG=$SCONE_FSPF_TAG" \
    -e "CAS_ADDR=$CAS_ADDR" \
    -e "CAS_MRENCLAVE=$CAS_MRENCLAVE" \
    -v "$CAS_SESSION_FOLDER:/cas_session" \
    -v "$SCONE_SCRIPTS_FOLDER/:/scone_scripts" \
    "registry.scontain.com:5050/sconecuratedimages/apps:python-3.7.3-alpine3.10-scone5.3.0" \
    "/scone_scripts/generate_session.sh"

# Finally, build the container image.
# Build the Docker image.
docker build "$SCRIPT_FOLDER" \
    -t "openehr-prov-service-scone"

# Generate the script to run locally, without LAS and CAS.
cat > "$SCRIPT_FOLDER/run-sim.sh" <<EOF
#!/usr/bin/env bash

# Run the container
docker run -it --rm \
    --name "openehr-prov-service" \
    --env-file "$SOURCE_FOLDER/.env" \
    -e "SCONE_MODE=sim" \
    -e "SCONE_FSPF=/fspf/fspf.pb" \
    -e "SCONE_FSPF_KEY=$SCONE_FSPF_KEY" \
    -e "SCONE_FSPF_TAG=$SCONE_FSPF_TAG" \
    --network host \
    "openehr-prov-service-scone"
EOF
chmod +x "$SCRIPT_FOLDER/run-sim.sh"
