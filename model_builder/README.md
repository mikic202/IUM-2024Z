Tworzenie modelu scripted:

model_scripted = torch.jit.script(model)
model_scripted.save('model_scripted.pt')


torch-model-archiver --model-name test_model \
    --version 1.0 \
    --model-file ModelHandler.py \
    --serialized-file model_scripted.pt \
    --handler ModelHandler.py \
    --force


torchserve --start --model-store . --models name=test_model.mar


curl -X POST http://127.0.0.1:8080/predictions/test_model \
     -H "Content-Type: application/json" \
     -d '{"data": [1.0, 2.0, 3.0, 5.9, 880]}'
