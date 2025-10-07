#!/usr/bin/env bash
set -e -o pipefail


bail() {
    if [[ $# -gt 0 ]]; then
        >&2 echo "Error: $*"
    fi
    exit 1
}

SCRIPT_PATH="$1"

source="$(tq -r ".sdk.source" -f Twoliter.lock)"
version="$(tq -r ".sdk.version" -f Twoliter.lock)"
_name="$(tq -r ".sdk.name" -f Twoliter.lock)"
_registry="${source%/*}"

registry="$(tq -r ".bottlerocket.bottlerocket-sdk.registry" -f Twoliter.override 2>/dev/null || echo "$_registry")"
name="$(tq -r ".bottlerocket.bottlerocket-sdk.name" -f Twoliter.override 2>/dev/null || echo "$_name")"

SDK="${registry}/${name}:v${version}"

docker run --rm \
    -v "$(pwd):/bottlerocket-kernel-kit" \
    --user "$(id -u):$(id -g)" \
    "${SDK}" \
    bash "${SCRIPT_PATH}"

