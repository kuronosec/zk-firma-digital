#!/bin/bash

set -e  # Exit on any error
set -u  # Treat unset variables as an error

#Versioning - Modify this per release
RELEASE_VERSION="0.5"
EXPECTED_SHA256="f7924230256b432a755746f7e86455f292f4e2659acc1f46e6db09c08c04b407"

# Download dependencies to the target dir.
REQUIRED_SYS_LIBS=("pcscd" "libccid" "libxcb-xinerama0" "libpcre3" "curl" "npm" "nodejs" "pcsc-tools" "libasedrive-usb")
REQUIRED_NPM_LIBS=("snarkjs")
SAKUNDI_URL="https://app.sakundi.io:9090/"
ZK_PACKAGE="zk-firma-digital_${RELEASE_VERSION}_amd64.deb"
DOWNLOAD_LINK=${SAKUNDI_URL}${ZK_PACKAGE}
TMP_DIR='/tmp/zk-firma-digital/'


# Detect the package manager
detect_package_manager() {
    if command -v apt-get > /dev/null; then
        echo "apt-get"
    else
        echo "Unsupported package manager" >&2
        exit 1
    fi
}
#check OS libs
check_and_install_libs(){
    echo "Checking required system libs"
    local installed_libs=()
    local missing_libs=()
    for dep in "${REQUIRED_SYS_LIBS[@]}"; do
        if dpkg -l | grep -q "$dep"; then 
            installed_libs+=("$dep")
        else
            missing_libs+=("$dep")
        fi
    done
    echo "Required libs that are already satisfied: ${installed_libs[*]}"
    echo "Required & missing libs: ${missing_libs[*]}"
    for dep in "${missing_libs[@]}"; do
        install_system_libs $(detect_package_manager) $dep
    done
}
# Install OS dependencies based on the package manager
install_system_libs() {
    local pkg_manager="$1"
    local library="$2"
    case "$pkg_manager" in
        apt-get)
            echo "Installing: $2"
            sudo apt-get install -y $2
            ;;
        npm)
            echo "Installing: $2"
            sudo npm install -g $2
            ;;
        *)
            echo "Unsupported package manager: $pkg_manager" >&2
            exit 1
            ;;
    esac
}
# Install npm dependencies
check_and_install_npm_libs(){
    echo "Checking required node libs"
    local installed_libs=()
    local missing_libs=()
    for lib in "${REQUIRED_NPM_LIBS[@]}"; do
        if npm list -g --depth=0 | grep -qw "$lib"; then 
            installed_libs+=("$lib")
        else
            missing_libs+=("$lib")
        fi
    done
    echo "Required npm libs that are already satisfied: ${installed_libs[*]}"
    echo "Required & missing  npm libs: ${missing_libs[*]}"
    for lib in "${missing_libs[@]}"; do
        install_system_libs npm $lib
    done
}


# Make sure the checksum matches
validate_sha256(){
    echo "Validating SHA256 checksum"
    local actual_sha256
    actual_sha256=$(sha256sum "${TMP_DIR}${ZK_PACKAGE}" | awk '{print $1}')

    if [[ "$actual_sha256" == "$EXPECTED_SHA256" ]]; then
        echo "SHA256 is valid"
    else 
        echo "SHA256 is invalid. Expected $EXPECTED_SHA256, Got: $actual_sha256"
        exit 1
    fi
}

# Trigger the download for the .deb package
download_zkfirma(){
    echo "Initializing download..."
    wget -P $TMP_DIR $DOWNLOAD_LINK 
    echo "Download complete. Saved at $TMP_DIR"
}

# check if the .deb package exits.
check_zk_package(){
    if [[ -f "${TMP_DIR}${ZK_PACKAGE}" ]]; then
        echo "$ZK_PACKAGE already exists." 
        validate_sha256
    else
        echo "$ZK_PACKAGE does not exist. "
        download_zkfirma
        validate_sha256 
    fi
}

#Temp dir to download the required files for installation.
create_temp_dir() {
    if [[ ! -d $TMP_DIR ]]; then 
        echo "Creating $TMP_DIR"
        mkdir $TMP_DIR
    fi
}

# Will install the actual .deb package
install_zk_firma(){
    create_temp_dir
    check_zk_package
    if [[ -f "${TMP_DIR}${ZK_PACKAGE}" ]]; then
        echo "$ZK_PACKAGE exists. Installing..." 
        sudo dpkg -i ${TMP_DIR}$ZK_PACKAGE
    else
        echo "$ZK_PACKAGE was not found. Aborting installation." 
        exit 1
    fi
}

# Main function
main() {
    echo "Initializing automatic install..."
    check_and_install_libs
    check_and_install_npm_libs
    install_zk_firma
    echo "Installation completed successfully!"
    echo "To execute run the following command: /usr/share/zk-firma-digital/zk-firma-digital.bin"
}

main


