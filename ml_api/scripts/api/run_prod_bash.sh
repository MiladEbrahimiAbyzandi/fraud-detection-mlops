#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
SRC_DIR="$BASE_DIR/src"

echo "BASE_DIR: $BASE_DIR"
echo "SRC_DIR: $SRC_DIR"    

# Load environment variables from .env file
envFile="$SRC_DIR/.env"
if [ -f "$envFile" ]; then
    export $(cat "$envFile" | grep -v '^#' | xargs)
fi

PORT=80

echo "# Running fraud-detection-ml-api in production mode"

uvicorn src.app:app --host=0.0.0.0 --port $PORT --reload 