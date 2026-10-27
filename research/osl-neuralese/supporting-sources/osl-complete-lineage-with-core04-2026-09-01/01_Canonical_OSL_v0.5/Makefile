SHELL := /bin/bash
JOB := operator_symbolic_ai_language_v0.5
PDF := $(JOB).pdf
SOURCE_DATE_EPOCH := 1787616000
export SOURCE_DATE_EPOCH
export FORCE_SOURCE_DATE := 1
export TZ := UTC
export PYTHONDONTWRITEBYTECODE := 1
export PYTHONPATH := reference

.PHONY: all rebuild evidence test syntax preflight metadata verify clean

all: $(PDF)

$(PDF): main.tex sections/osl_core_language.tex sections/osl_core_examples.tex sections/osl_core_semantics.tex sections/osl_core_v02.tex sections/osl_core_v03.tex
	latexmk -pdf -interaction=nonstopmode -halt-on-error -jobname=$(JOB) main.tex

rebuild:
	latexmk -pdf -g -interaction=nonstopmode -halt-on-error -jobname=$(JOB) main.tex

evidence:
	python reference/generate_v03_evidence.py >/tmp/osl_v03_certificate_index.json
	python reference/verify_osl_core_v03.py --output V03_UNIFIED_VERIFICATION.json >/tmp/osl_v03_unified.json

test:
	python reference/generate_test_report.py >/tmp/osl_v03_test_report.json

syntax:
	python reference/verify_sources.py

preflight: $(PDF)
	python reference/generate_pdf_preflight.py >/tmp/osl_v05_pdf_preflight.json

metadata: evidence test preflight
	python reference/build_release_metadata.py >/tmp/osl_v05_metadata.json

verify: rebuild evidence test syntax preflight metadata
	python verify_release.py
	@echo "OPERATOR_SYMBOLIC_AI_V05_VERIFY_PASS"

clean:
	latexmk -C -jobname=$(JOB) main.tex || true
	rm -f $(PDF) $(JOB).aux $(JOB).fdb_latexmk $(JOB).fls $(JOB).log $(JOB).out $(JOB).toc
