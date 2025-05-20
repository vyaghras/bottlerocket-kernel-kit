#!/usr/bin/env bash

set -e -o pipefail

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

Extract kernel configurations from an RPM, merge with Bottlerocket's, and write out to a file, per architecture (x86_64 and aarch64).
Run from the top-level bottlerocket-kernel-kit directory with the following parameters:
    -r RPM_FILE    Path to RPM file
    -h             Display this help message

Dependencies:
    - docker
    - rpm2cpio
    - cpio
    - tar
    - tq
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
    hash tq || usage_error "DEPENDENCY ERROR: Please cargo install tomlq somewhere in your PATH"
}

# Get the SDK version from workspace Twoliter.toml and Twoliter.override, if provided.
# Assumes running in the top level of the project and `tq` on $PATH.
resolve_bottlerocket_sdk() {
    # Inspect Twoliter.lock file for [sdk] section source
    source="$(tq -r ".sdk.source" -f Twoliter.lock)"
    version="$(tq -r ".sdk.version" -f Twoliter.lock)"
    _name="$(tq -r ".sdk.name" -f Twoliter.lock)"
    # Trim from last slash, e.g. public.ecr.aws/bottlerocket/bottlerocket-sdk:v0.61.0 -> public.ecr.aws/bottlerocket
    _registry="${source%/*}"

    # Check Twoliter.override to get the registry. For simplicity, assume overrides are only against named project named bottlerocket-sdk
    registry="$(tq -r ".bottlerocket.bottlerocket-sdk.registry" -f Twoliter.override 2>/dev/null || echo "$_registry")"
    name="$(tq -r ".bottlerocket.bottlerocket-sdk.name" -f Twoliter.override 2>/dev/null || echo "$_name")"

    # Form the final SDK
    echo "${registry}/${name}:v${version}"
}

# expect $pwd to be packages/kernel-${kver}
merge_kernel_configs() {
    rpm_file=$1
    sdk_image=$2
    kernel_path=$PWD

    version="$(rpm --query --nosignature --queryformat '%{VERSION}' "${rpm_file}")"
    majorminor=${version%.*} # Trim after last '.', e.g. 6.1.132 -> 6.1
    if [ "${majorminor}" == "6.12" ]; then
        # kernel 6.12 has a patch file that is not applied to the kernel sources, so
        # only pick up the 1000-series kernel patches for our purposes here.
        readarray -t br_patches < <(find "${kernel_path}" -maxdepth 1 -name "10*.patch")
        spec_file="kernel6.12.spec"
        microcode_file="config-microcode-6-12"
    else
        readarray -t br_patches < <(find "${kernel_path}" -maxdepth 1 -name "*.patch")
        spec_file="kernel.spec"
        microcode_file="config-microcode"
    fi

    tmpdir=$(mktemp -d)
    cp "${rpm_file}" "${tmpdir}/"
    pushd "${tmpdir}" || bail "Could not move around"

    rpm2cpio "${rpm_file}" | cpio -iu {,./}linux-"${version}".tar{,.xz} {,./}config-x86_64 {,./}config-aarch64 {,./}"*.patch" {,./}"${spec_file}"
    # Upstream source is either xz compressed tarball or plain tarball
    if [ -f "./linux-${version}.tar" ]; then
        tar -xof linux-"${version}".tar; rm linux-"${version}".tar
    else
        tar -xof linux-"${version}".tar.xz; rm linux-"${version}".tar.xz
    fi

    # Find patch ordering based on the upstream SRPM and apply in that order
    readarray -t patches < <(grep -P "^Patch\d+" "${spec_file}" | sort -n -k1.6 | grep -oP "^Patch\d+: \K.*\.patch$" "${spec_file}")

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
        microcode_cfg="${kernel_path}/../microcode/${microcode_file}"
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
            --name "${arch}-kernel-${version}-config-merger" \
            "${sdk_image}" \
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

rpm_file=$(realpath "${rpm_file}")

# Check if the RPM file exists
if [ ! -f "${rpm_file}" ]; then
    bail "RPM file not found: ${rpm_file}"
fi

# Check dependencies
check_dependencies

# Get SDK image from Twoliter.lock and/or Twoliter.override
sdk_image=$(resolve_bottlerocket_sdk)

# Parse RPM file for kernel version (6.1, 6.12, etc.)
kver=$(rpm --query --nosignature --queryformat '%{VERSION}' "${rpm_file}" | sed 's/\.[^.]*$//')

# pushd into kernel dir
pushd packages || bail "Could not move into packages"
pushd kernel-"${kver}" || bail "Could not move into packages/kernel-${kver}"

# Merge configs
merge_kernel_configs "${rpm_file}" "${sdk_image}"

# Exit kernel-${kver}/ dir
popd  || bail "Could not move around - 'popd' failed."
# Exit packages/ dir
popd  || bail "Could not move around - 'popd' failed."
