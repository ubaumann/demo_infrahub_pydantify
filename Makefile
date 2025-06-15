help:
	@echo  'Start or Stop Infrahub:'
	@echo  ''
	@echo  '  setup           - Start Infrahub and Prefect'
	@echo  '  stop            - Stop Infrahub and Prefect'
	@echo  '  destory         - Destorys Infrahub and Prefect'
	@echo  ''

.PHONY: help Makefile

%: Makefile
	$(MAKE) -C setup $@