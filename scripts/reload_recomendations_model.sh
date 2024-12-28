echo Make sure that the model is in the right place app is running

MODEL_FILE=$1

curl -X DELETE "http://localhost:8081/models/recomendations_model"
curl -X POST "http://localhost:8081/models?url=$MODEL_FILE&model_name=recomendations_model"
