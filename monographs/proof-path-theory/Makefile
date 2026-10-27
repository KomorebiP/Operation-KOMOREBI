.PHONY: install test figures paper verify verify-lean

install:
	python -m pip install -e ".[release]" --no-build-isolation

test:
	PYTHONPATH=src python -m pytest -o addopts='' -q

figures:
	python scripts/design_figures.py

paper: figures
	cd docs && pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex && pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex && pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex

verify: test
	PYTHONPATH=src python scripts/deep_validation.py
	PYTHONPATH=src python scripts/verify_bridge.py
	PYTHONPATH=src python scripts/check_recovery_extension.py
	PYTHONPATH=src python scripts/check_trace_exchange.py
	python scripts/verify_publication_edition.py

verify-lean:
	python scripts/verify_lean.py --runtime "$(RUNTIME)"
