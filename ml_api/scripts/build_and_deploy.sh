#!/bin/bash
set -euo pipefail
set -E
trap 'rc=$?; [ $rc -ne 0 ] && echo "ERROR $rc at $BASH_COMMAND" >&2; exit $rc' ERR


SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

echo "Loading environment variables from .env.build file..."
set -a
source "$SCRIPT_DIR/.env.build"
set +a

echo "Setting gcloud default project to $GCP_PROJECT_ID"
gcloud config set project $GCP_PROJECT_ID

source "$SCRIPT_DIR/_1_build_and_push_docker_image.sh"