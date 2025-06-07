help:
	@echo  'Start or Stop Infrahub:'
	@echo  ''
	@echo  '  setup           - Start Infrahub'
	@echo  '  destory         - Stop Infrahub'
	@echo  ''

.PHONY: help Makefile

%: Makefile
	$(MAKE) -C infrahub $@