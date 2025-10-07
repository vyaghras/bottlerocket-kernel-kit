#!/usr/bin/env bash

set -e -o pipefail

KERNEL_KIT_DIR="/bottlerocket-kernel-kit"
MICROCODE_DIR="${KERNEL_KIT_DIR}/packages/microcode"

# Usage information
usage() {
    cat << EOF
Usage: $0

This script generates and validates full kernel configurations for all available
kernel versions in the Bottlerocket kernel kit.

IMPORTANT: This script is designed to run inside the Bottlerocket SDK container
and should typically be invoked via the Makefile target:

    make full-config

Running this script directly outside the SDK container will fail because it
requires the proper build environment and mounted paths.

The script will:
1. Discover all kernel-* packages with available RPMs
2. Extract and patch kernel sources
3. Merge Bottlerocket-specific configurations
4. Generate full configuration files
5. Validate that all required configs are present

EOF
}

# Common error handling
bail() {
    if [[ $# -gt 0 ]]; then
        >&2 echo "Error: $*"
    fi
    exit 1
}

# Function to merge kernel configurations for a specific kernel version
merge_kernel_configs() {
    local version="$1"
    local majorminor="$2"
    local tmpdir="$3"

    local kernel_package_dir="${KERNEL_KIT_DIR}/packages/kernel-${majorminor}"

    if [ "${majorminor}" == "6.12" ]; then
        # kernel 6.12 has a patch file that is not applied to the kernel sources, so
        # only pick up the 1000-series kernel patches for our purposes here.
        readarray -t br_patches < <(find "${kernel_package_dir}" -maxdepth 1 -name "10*.patch")
        spec_file="kernel6.12.spec"
        microcode_file="config-microcode-6-12"
    else
        readarray -t br_patches < <(find "${kernel_package_dir}" -maxdepth 1 -name "*.patch")
        spec_file="kernel.spec"
        microcode_file="config-microcode"
    fi

    local kernel_path="${kernel_package_dir}"

    pushd "${tmpdir}" || bail "Unable to enter temporary directory"

    rpm2cpio kernel-source.rpm | cpio -iu {,./}linux-"${version}".tar{,.xz} {,./}config-x86_64 {,./}config-aarch64 {,./}"*.patch" {,./}"${spec_file}"

    # Upstream source is either xz compressed tarball or plain tarball
    if [ -f "./linux-${version}.tar" ]; then
        tar -xof linux-"${version}".tar; rm linux-"${version}".tar
    else
        tar -xof linux-"${version}".tar.xz; rm linux-"${version}".tar.xz
    fi

    # Find upstream patch ordering based on the upstream SRPM so we can apply in that order
    readarray -t patches < <(grep -P "^Patch\d+" "${spec_file}" | sort -n -k1.6 | grep -oP "^Patch\d+: \K.*\.patch$" "${spec_file}")

    # Enter the source directory extracted from the tarball and patch
    pushd "linux-${version}" || bail "Could not move into linux-${version}"

    # Patches from the upstream
    for patch in "${patches[@]}"; do
        patch -p1 <"../$patch"
    done

    # Patches from bottlerocket
    for patch in "${br_patches[@]}"; do
        echo "Applying bottlerocket patch ${patch}"
        patch -p1 <"$patch"
    done

    popd || bail "Could not move around - 'popd' back to /work failed. Lets stop before we break anything further."

    for arch in "x86_64" "aarch64"; do
        br_cfg="${kernel_path}/config-bottlerocket"
        br_cfg_arch="${kernel_path}/config-bottlerocket-${arch}"
        microcode_cfg="${MICROCODE_DIR}/${microcode_file}"

        pushd "linux-${version}" || bail "Could not move into linux-${version}"

        if [ "${arch}" = "aarch64" ]; then
            karch="arm64"
            script_args=("../config-${arch}" "${br_cfg}" "${br_cfg_arch}")
        elif [ "${arch}" = "x86_64" ]; then
            karch="x86"
            script_args=("../config-${arch}" "${microcode_cfg}" "${br_cfg}" "${br_cfg_arch}")
        fi

        ARCH=${karch} \
        CROSS_COMPILE=/usr/bin/${arch}-bottlerocket-linux-gnu- \
        KCONFIG_CONFIG=bottlerocket_${arch}_defconfig \
        ./scripts/kconfig/merge_config.sh "${script_args[@]}"

        mv -f "bottlerocket_${arch}_defconfig" "${kernel_path}/config-full-bottlerocket-${arch}" || bail "Failed to create config-full-bottlerocket-${arch}"
        popd || bail "Could not move around - 'popd' failed in merge_config loop. Lets stop before we break anything further."
    done

    popd || bail "Could not return from temporary directory"
}

# Function to validate kernel configurations (similar to validate_config.sh)
validate_kernel_configs() {
    local version="$1"
    local majorminor="$2"
    local errors=0
    local kernel_path="${KERNEL_KIT_DIR}/packages/kernel-${majorminor}"

    for arch in x86_64 aarch64; do
        echo "=== Validating kernel-${majorminor} ${arch} ==="

        # Check if files exist
        if [[ ! -f "${kernel_path}/config-bottlerocket" ]]; then
            echo "❌ Missing config-bottlerocket"
            (( ++errors ))
            continue
        fi
        if [[ ! -f "${kernel_path}/config-bottlerocket-${arch}" ]]; then
            echo "❌ Missing config-bottlerocket-${arch}"
            (( ++errors ))
            continue
        fi
        if [[ ! -f "${kernel_path}/config-full-bottlerocket-${arch}" ]]; then
            echo "❌ Missing config-full-bottlerocket-${arch}"
            (( ++errors ))
            continue
        fi

        # Extract config lines (ignoring comments by default to avoid issues with removed kernel options)
        local common_configs
        common_configs=$(grep "^CONFIG_" "${kernel_path}/config-bottlerocket" | sort)
        local arch_configs
        arch_configs=$(grep "^CONFIG_" "${kernel_path}/config-bottlerocket-${arch}" | sort)
        local full_configs
        full_configs=$(grep "^CONFIG_" "${kernel_path}/config-full-bottlerocket-${arch}" | sort)

        # Check common configs
        local missing_common
        missing_common=$(comm -23 <(echo "$common_configs") <(echo "$full_configs"))
        # Check arch-specific configs
        local missing_arch
        missing_arch=$(comm -23 <(echo "$arch_configs") <(echo "$full_configs"))

        if [[ -n "$missing_common" ]]; then
            echo "❌ Missing common configs:"
            echo "$missing_common"
            (( ++errors ))
        fi

        if [[ -n "$missing_arch" ]]; then
            echo "❌ Missing arch-specific configs:"
            echo "$missing_arch"
            (( ++errors ))
        fi

        if [[ -z "$missing_common" && -z "$missing_arch" ]]; then
            echo "✅ All configs present for ${arch}"
        fi
    done

    if (( errors == 0 )); then
        echo -e "\n🎉 All kernel config validations passed!"
    else
        echo -e "\n💥 Some kernel config validations failed!"
        bail "Kernel configuration validation failed"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
    shift
done

# Ensure this script is run within the Bottlerocket SDK container
if [[ ! -d "${KERNEL_KIT_DIR}" ]]; then
    usage
    bail
fi

# In kernel kit automation, CodePipeline updates each kernel separately.
# This script processes only kernels that have available RPM files,
# skipping any kernel packages without corresponding source RPMs.
kernels_to_process=()
for kernel_dir in "${KERNEL_KIT_DIR}/packages"/kernel-*; do
    if [[ -d "${kernel_dir}" ]]; then
        kernel_pkg=$(basename "${kernel_dir}")
        # In CodePipeline, only one RPM exists per kernel package, but during development
        # multiple RPMs can coexist. Use version sorting to select the latest RPM.
        # Sorting rules: https://www.gnu.org/software/coreutils/manual/html_node/sort-invocation.html
        rpm_file=$(find "${kernel_dir}" -name "kernel*.src.rpm" | sort -V | tail -1)
        if [[ -n "${rpm_file}" ]]; then
            kernels_to_process+=("${kernel_pkg}")
            echo "Found RPM for ${kernel_pkg}: $(basename "${rpm_file}")"
        else
            echo "No RPM found for ${kernel_pkg}, skipping"
        fi
    else
        bail "No Kernel directory found for ${kernel_dir}"
    fi
done

if [[ ${#kernels_to_process[@]} -eq 0 ]]; then
    bail "No kernel RPMs found in any package directory"
fi

# Process available kernels
for kernel_pkg in "${kernels_to_process[@]}"; do
    echo "Processing ${kernel_pkg}..."

    tmpdir=$(mktemp -d)

    pushd "${tmpdir}" || bail "Unable to enter temporary directory"

    rpm_file=$(find "${KERNEL_KIT_DIR}/packages/${kernel_pkg}" -name "kernel*.src.rpm" | head -1)

    cp "${rpm_file}" kernel-source.rpm

    version="$(rpm --query --nosignature --queryformat '%{VERSION}' kernel-source.rpm)"
    majorminor=${version%.*} # Trim after last '.', e.g. 6.1.132 -> 6.1

    merge_kernel_configs "${version}" "${majorminor}" "${tmpdir}"

    echo "Validating ${kernel_pkg} configurations..."
    validate_kernel_configs "${version}" "${majorminor}" || bail "Validation failed for ${kernel_pkg}"

    popd || bail "Could not return from temporary directory"
done
