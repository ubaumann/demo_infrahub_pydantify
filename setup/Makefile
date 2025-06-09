.PHONY: setup
setup:
	docker compose -f docker-compose.infrahub.yaml -f docker-compose.prefect.yaml -f docker-compose.override.yaml up -d 

.PHONY: destroy
destroy:
	docker compose -f docker-compose.infrahub.yaml -f docker-compose.prefect.yaml -f docker-compose.override.yaml down