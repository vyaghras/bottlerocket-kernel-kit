#!/usr/bin/env bash
set -e -o pipefail

TQ_IMAGE=ghcr.io/mdm-code/tq:v2.4.0

bail() {
    if [[ $# -gt 0 ]]; then
        >&2 echo "Error: $*"
    fi
    exit 1
}

find_sdk() {
  docker run --rm \
      -v "$(pwd):/bottlerocket-kernel-kit:ro" \
      --user "$(id -u):$(id -g)" \
      --network none \
      "${TQ_IMAGE}" \
      tq -q "[sdk][source]" /bottlerocket-kernel-kit/Twoliter.lock
}

SCRIPT_PATH="$1"

if [[ -z "${SDK}" ]]; then
  echo "Retriving SDK from Twoliter.lock"
  SDK="$(find_sdk)"
fi

echo "Using SDK: ${SDK} to run the provided script"

docker run --rm \
    -v "$(pwd):/bottlerocket-kernel-kit" \
    --user "$(id -u):$(id -g)" \
    "${SDK}" \
    bash "${SCRIPT_PATH}"

