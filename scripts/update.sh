#!/usr/bin/bash

# Made with <3 by Doobs in Miami, FL. 03/17/2025
# Modified by F. Mendonca

PATCH_URL=${PATCH_URL:-http://15.235.112.186:9000/patch/latest.zip}
PATCH_TEST_URL=${PATCH_TEST_URL:-http://15.235.112.186:9000/patch/dev.zip}

CONFIG_PATH="/spellbreak-server/Instances/GameServer/config.ini"
PATCH_URL=$PATCH_URL
PATCH_TEST_URL=$PATCH_TEST_URL
PATCH_DIR="/spellbreak-server/BaseServer/g3/Content/Paks"
PATCH_FILE="$PATCH_DIR/latest.zip"
PATCH_TESTING_FILE="$PATCH_DIR/dev.zip"

# Ensure the patch directory exists
mkdir -p "$PATCH_DIR"

# Skip patch installation if PATCH_ENV is set to "vanilla"
if [ "$PATCH_ENV" = "vanilla" ]; then
    echo "PATCH_ENV is set to vanilla. Skipping patch installation."
else
    # Determine which patch to deploy based on PATCH_ENV
    if [ "$PATCH_ENV" = "dev" ]; then
        PATCH_TO_DEPLOY="$PATCH_TESTING_FILE"
        PATCH_SOURCE_URL="$PATCH_TEST_URL"
        echo "Deployment mode: dev"
    else
        PATCH_TO_DEPLOY="$PATCH_FILE"
        PATCH_SOURCE_URL="$PATCH_URL"
        echo "Deployment mode: production"
    fi

    # Download and extract the selected patch
    echo "Downloading patch from $PATCH_SOURCE_URL..."
    if curl -fSL "$PATCH_SOURCE_URL" -o "$PATCH_TO_DEPLOY"; then
        echo "Extracting patch..."
        unzip -o "$PATCH_TO_DEPLOY" -d "$PATCH_DIR"
        echo "Patch extracted successfully."

        # Delete the zip file after extraction
        rm -f "$PATCH_TO_DEPLOY"
    else
        echo "Failed to download patch. Check network or URL."
    fi
fi
