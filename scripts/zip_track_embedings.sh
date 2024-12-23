#!/bin/bash

mkdir -p model_api/recomendation_models

if [ "$2" = "force" ]; then
    COUNT=$(ls model_api/track_embeding_models | wc -l)
    NUMBER_OF_VERSIONS=$(( COUNT - 1 > 0 ? COUNT - 1 : 0 ))
else
    NUMBER_OF_VERSIONS=$(ls model_api/track_embeding_models | wc -l)
fi

MODEL_NAME="track_embeding_v$NUMBER_OF_VERSIONS"

torch-model-archiver --model-name $MODEL_NAME \
    --version $NUMBER_OF_VERSIONS \
    --model-file model_builder/TrackEmbedingsHandler.py \
    --serialized-file $1 \
    --handler model_builder/TrackEmbedingsHandler.py \
    --force \
    --export-path model_api/track_embeding_models
