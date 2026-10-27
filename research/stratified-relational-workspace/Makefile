PYTHON ?= python3

.PHONY: all build test verify package clean

all: verify

build:
	$(PYTHON) scripts/repo.py build

test:
	$(PYTHON) verification/run_all.py

verify:
	$(PYTHON) scripts/repo.py verify

package:
	$(PYTHON) scripts/repo.py package --strict

clean:
	$(PYTHON) scripts/repo.py clean
