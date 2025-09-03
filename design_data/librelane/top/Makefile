all: top copy-final

PDK_ROOT ?= ~/.ciel
PDK ?= ihp-sg13g2

RUN_TAG = $(shell ls runs/ -1 | tail -n 1)
TOP = top

top:
	librelane config.yaml --manual-pdk 
.PHONY: top

copy-final:
	rm -rf final/
	cp -r runs/${RUN_TAG}/final final/
.PHONY: copy-final

view-openroad:
	librelane config.yaml --manual-pdk --last-run --flow OpenInOpenROAD
.PHONY: view-openroad

view-klayout:
	librelane config.yaml --manual-pdk --last-run --flow OpenInOpenROAD
.PHONY: view-klayout
