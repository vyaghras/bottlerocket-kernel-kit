#!/usr/bin/env bash

#
# Common error handling
#

# Cleanup all tmp files/directories
cleanup() {
    rm -rf "$tmpdir"
}

trap cleanup INT EXIT

bail() {
    if [[ $# -gt 0 ]]; then
        >&2 echo "Error: $*"
    fi
    exit 1
}

# Function to display usage information
usage() {
    cat << EOF
Usage: $(basename "$0") -r RPM_FILE

Merge kernel configurations with the following parameters:
    -r RPM_FILE    Path to RPM file
    -h             Display this help message

Dependencies:
    - docker
    - rpm2cpio
    - cpio
    - tar
EOF
}

usage_error() {
    >&2 usage
    bail "$1"
}

check_dependencies() {
    hash rpm2cpio || usage_error "DEPENDENCY ERROR: Please install rpm2cpio somewhere in your PATH"
    hash cpio || usage_error "DEPENDENCY ERROR: Please install cpio somewhere in your PATH"
    hash tar || usage_error "DEPENDENCY ERROR: Please install tar somewhere in your PATH"
    hash docker || usage_error "DEPENDENCY ERROR: Please install docker somewhere in your PATH"
}

# expect $pwd to be packages/kernel-${kver}
merge_kernel_configs() {
    rpm_file=$1
    kernel_path=$PWD

    version="$(rpm --query --nosignature --queryformat '%{VERSION}' "${rpm_file}")"
    # kernel 6.12 has a patch file that is not applied to the kernel sources, so
    # only pick up the 1000-series kernel patches for our purposes here.
    readarray -t br_patches < <(find "${kernel_path}" -maxdepth 1 -name "10*.patch")

    tmpdir=$(mktemp -d)
    cp "${rpm_file}" "${tmpdir}/"
    pushd "${tmpdir}" || bail "Could not move around"

    rpm2cpio "${rpm_file}" | cpio -iu {,./}linux-"${version}".tar.xz {,.}config-x86_64 {,.}config-aarch64 {,./}"*.patch" {,./}kernel6.12.spec
    tar -xof linux-"${version}".tar.xz; rm linux-"${version}".tar.xz

    # Find patch ordering based on the upstream SRPM and apply in that order
    readarray -t patches < <(grep -P "^Patch\d+" kernel6.12.spec | sort -n -k1.6 | grep -oP "^Patch\d+: \K.*\.patch$" kernel6.12.spec)

    pushd "linux-${version}" || bail "Could not move into linux-${version}"

    # Patches from the upstream
    for patch in "${patches[@]}"; do
        patch -p1 <"../$patch"
    done

    # Patches from bottlerocket
    for patch in "${br_patches[@]}"; do
        echo "Applying ${patch}"
        patch -p1 <"$patch"
    done

    popd || bail "Could not move around - 'popd' failed. Lets stop before we break anything further."

    for arch in "x86_64" "aarch64"; do

        br_cfg="${kernel_path}/config-bottlerocket"
        microcode_cfg="${kernel_path}/../microcode/config-microcode-6-12"
        al_cfg="${PWD}/config-${arch}"
        linux_src="${PWD}/linux-${version}"

        pushd "linux-${version}" || bail "Could not move into linux-${version}"

        if [ "${arch}" = "aarch64" ]; then
            karch="arm64"
            script_args=("../config-${arch}" "../config-bottlerocket")
        elif [ "${arch}" = "x86_64" ]; then
            karch="x86"
            script_args=("../config-${arch}" "../config-microcode" "../config-bottlerocket")
        fi

        # mount config files and start the sdk docker container
        docker run --rm \
            -v "${br_cfg}":/config-bottlerocket \
            -v "${microcode_cfg}":/config-microcode \
            -v "${al_cfg}":/config-${arch} \
            -v "${linux_src}":/linux-"${version}" \
            -e ARCH="${karch}" \
            -e CROSS_COMPILE=/usr/bin/${arch}-bottlerocket-linux-gnu- \
            -e KCONFIG_CONFIG=bottlerocket_${arch}_defconfig \
            -w /linux-"${version}" \
            --name ${arch}-config-merger public.ecr.aws/bottlerocket/bottlerocket-sdk:v0.60.0 \
            ./scripts/kconfig/merge_config.sh \
            "${script_args[@]}"

        mv -f "bottlerocket_${arch}_defconfig" "${kernel_path}/config-full-bottlerocket-${arch}"
        popd || bail "Could not move around - 'popd' failed. Lets stop before we break anything further."
    done

    popd || bail "Could not move around - 'popd' failed. Lets stop before we break anything further."

}

################################################################################
# START MAIN CONTROL FLOW
################################################################################

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--rpm-file)
            shift; rpm_file="$1" ;;
        *)
            usage_error "Invalid option '$1'" ;;
    esac
    shift
done

# Verify all required parameters are provided
if [ -z "${rpm_file}" ]; then
    echo "Error: Missing required parameters"
    usage
    exit 1
fi

# Check dependencies
check_dependencies

merge_kernel_configs "${rpm_file}"
