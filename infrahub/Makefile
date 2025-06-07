.PHONY: setup
setup:
	 docker compose up -d
	 infrahubctl schema load simple_interface_schema.yaml

.PHONY: destroy
destroy:
	 docker compose down