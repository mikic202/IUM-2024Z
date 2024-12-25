#!/bin/bash

MAIN_MODEL_STORE=main_models

MODEL_DIR="track_embeding_models"
RECOMANDATIONS_MODEL_DIR="recomendation_models"

HIGHEST_VERSION_FILE=$(ls track_embeding_models | sort -V | tail -1)
HIGHEST_RECOMENDATION_VERSION_FILE=$(ls recomendation_models | sort -V | tail -1)

echo "Starting model server with model $HIGHEST_VERSION_FILE"
echo "Starting recomandation server with model $HIGHEST_RECOMENDATION_VERSION_FILE"

mkdir -p $MAIN_MODEL_STORE
cp -r $MODEL_DIR/$HIGHEST_VERSION_FILE $MAIN_MODEL_STORE/
cp -r $RECOMANDATIONS_MODEL_DIR/$HIGHEST_RECOMENDATION_VERSION_FILE $MAIN_MODEL_STORE/

torchserve --start --model-store $MAIN_MODEL_STORE --models embeding_model="$HIGHEST_VERSION_FILE" recomendations_model="$HIGHEST_RECOMENDATION_VERSION_FILE" --ts-config config.properties --disable-token-auth --enable-model-api

# prevent docker exit
tail -f /dev/null