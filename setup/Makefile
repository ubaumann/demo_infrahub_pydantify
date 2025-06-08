.PHONY: setup
setup:
	docker compose -f docker-compose.infrahub.yaml -f docker-compose.prefect.yaml up -d 

.PHONY: destroy
destroy:
	docker compose down