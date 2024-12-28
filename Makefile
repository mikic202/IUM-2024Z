CONFIG = Makefile.conf
include $(CONFIG)

package_embeding_model:
	@echo "Packaging embedding model"
	@./scripts/zip_track_embedings.sh $(EMBEDDING_MODEL_PATH)

package_recommendation:
	@echo "Packaging recommendation"
	@./scripts/zip_recomendation_model.sh $(RECOMMENDATION_MODEL_PATH)

change_recomendations_model:
	@echo "Changing recomendations model"
	@./scripts/reload_recomendations_model.sh $(RECOMMENDATION_MODEL)

change_embeding_model:
	@echo "Changing embeding model"
	@./scripts/reload_embeding_model.sh $(EMBEDDING_MODEL)