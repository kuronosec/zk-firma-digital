#!/bin/bash

set -e  # Exit on any error
set -u  # Treat unset variables as an error


#Node, Circom (And cargo & Rust) & SnarkJS within the host machine


# Download dependencies to the target dir.
REQUIRED_SYS_LIBS=("pcscd" "libccid" "libxcb-xinerama0" "libpcre3" "curl" "npm" "nodejs" "pcsc-tools" "libasedrive-usb") # nodejs npm
REQUIRED_NPM_LIBS=("snarkjs")
REQUIRED_DEPENDENCIES=("")

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



# check_dependencies(){
#     echo "Checking host dependencies"
#     local missing_deps()
#     for dep in "${REQUIRED_DEPENDENCIES[@]}"; do
#         if ! command -v "$dep" &>/dev/null; then
#             missing_deps+=("$dep")
#         fi
#     done

#     if [[ ${#missing_deps[@] -gt 0} ]]; then
#         echo "Missing dependencies: ${missing_deps[*]}"
#         # Take that list and install them.
#         exit 1
#     fi 
# }

#Temp dir to download the required files for installation.
create_temp_dir() {
    dir='/tmp/zk-firma-digital/'
    if [[ ! -d $dir ]]; then 
        echo "Creating $dir"
        mkdir /tmp/zk-firma-digital/
    fi
}



# Install the binary
install_binary() {
    local binary_path="$1"
    sudo install -m 0755 "$binary_path" /usr/local/bin/\<REPLACE\>
}

# Main function
main() {
    echo "Detecting package manager..."
    local pkg_manager
    pkg_manager=$(detect_package_manager)
    echo "Package manager detected: $pkg_manager"

    echo "Installing dependencies..."
    install_dependencies "$pkg_manager"

    echo "Installing binary..."
    install_binary "/binary path"

    echo "Installation completed successfully!"
}

# main "$@"
#check_and_install_libs
#check_and_install_npm_libs


# Some dependencies: Node, Circom, Gaudi, 
# Circom requires rust to be installed as well

# This script will check all the dependencies are met if not installed it will proceed with the installation.
# is going to install all the dependencies and also the ZK-firma digital binary.
# Might check the installer.iss to see if we can embed that there
# 


