PYTHON ?= python3
MANUSCRIPT := manuscript
MAIN_TEX := Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.tex
STANDALONE := standalone/Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.tex

.PHONY: setup check verify build full audit standalone clean package manifests visuals

setup:
	$(PYTHON) -m pip install -r requirements.txt

check:
	$(PYTHON) scripts/check_release.py

verify: check
	cd $(MANUSCRIPT) && $(PYTHON) verify_block15_lane_transport.py
	cd $(MANUSCRIPT) && $(PYTHON) verify_block16_holonomy_lane_transport.py
	cd $(MANUSCRIPT) && $(PYTHON) verify_block16_publication_audit.py

build:
	cd $(MANUSCRIPT) && ./Build.sh

full:
	cd $(MANUSCRIPT) && ./Build.sh --full

audit:
	cd $(MANUSCRIPT) && ./Build.sh --audit-only

standalone:
	cd standalone && latexmk -silent -pdf -interaction=nonstopmode -halt-on-error -file-line-error Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.tex

clean:
	cd $(MANUSCRIPT) && latexmk -C $(MAIN_TEX)
	cd standalone && latexmk -C Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.tex

package:
	$(PYTHON) scripts/package_release.py

manifests:
	$(PYTHON) scripts/generate_manifests.py

visuals:
	$(PYTHON) visuals/generate_large_domain_phase_diagrams.py --domain-size 1000 --dpi 500
