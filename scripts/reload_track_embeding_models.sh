echo Make sure that the model is in the right place and the app is running

MODEL_FILE=$1

curl -X DELETE "http://localhost:8081/models/embeding_model"
curl -X POST "http://localhost:8081/models?url=$MODEL_FILE&model_name=embeding_model"
