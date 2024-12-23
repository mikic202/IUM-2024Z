#!/bin/bash

MODEL_DIR="track_embeding_models"

HIGHEST_VERSION_FILE=$(ls track_embeding_models | sort -V | tail -1)

echo "Starting model server with model $HIGHEST_VERSION_FILE"

torchserve --start --model-store track_embeding_models --models embeding_model="$HIGHEST_VERSION_FILE" --ts-config config.properties --disable-token-auth

# prevent docker exit
tail -f /dev/null