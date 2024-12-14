#!/bin/bash

torchserve --start --model-store . --models name=test_model.mar --ts-config config.properties --disable-token-auth

# prevent docker exit
tail -f /dev/null