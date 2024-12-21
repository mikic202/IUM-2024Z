CONFIG = Makefile.conf
include $(CONFIG)

package_embeding_model:
	@echo "Packaging embedding model"
	@./scripts/zip_track_embedings.sh $(EMBEDDING_MODEL_PATH)

package_recommendation:
	@echo "Packaging recommendation"
	@./scripts/zip_recomendation_model.sh $(EMBEDDING_MODEL_PATH)