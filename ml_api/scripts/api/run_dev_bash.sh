#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
SRC_DIR="$BASE_DIR/src"

echo "SCRIPT_DIR: $SCRIPT_DIR"
echo "BASE_DIR: $BASE_DIR"
echo "SRC_DIR: $SRC_DIR"    


# Load environment variables from .env.local if it exists
if [ -f "$SCRIPT_DIR/../.env.local" ]; then
  echo "Loading environment variables from .env.local..."
  set -a
  source "$SCRIPT_DIR/../.env.local"
  set +a
else
  echo "Warning: .env.local file not found at $SCRIPT_DIR/../.env.local"
fi


echo "# Running fraud-detection-ml-api in dev mode"

uvicorn src.main:app --host=0.0.0.0 --port 8000 --reload 