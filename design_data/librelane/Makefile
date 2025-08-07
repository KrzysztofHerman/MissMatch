all: decoder copy-final

PDK_ROOT ?= ~/.ciel
PDK ?= ihp-sg13g2

RUN_TAG = $(shell ls runs/ -1 | tail -n 1)
TOP = decoder

decoder:
	librelane config.yaml --pdk $(PDK)
.PHONY: decoder

copy-final:
	rm -rf final/
	cp -r runs/${RUN_TAG}/final final/
.PHONY: copy-final

view-openroad:
	librelane config.yaml --pdk $(PDK) --last-run --flow OpenInOpenROAD
.PHONY: view-openroad

view-klayout:
	librelane config.yaml --pdk $(PDK) --last-run --flow OpenInOpenROAD
.PHONY: view-klayout
