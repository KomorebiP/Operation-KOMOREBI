# Evidence validator provenance

validate_manifest.py was transcribed from the installed mathbox computation-audit skill's scripts/validate_manifest.py, read in full through the skill resource interface on 26 September 2026. Three explanatory comment lines in the software-version branch were omitted. Its schema and validation logic are retained. It is an evidence-record validator, not the Lean proof checker.

run_recorded.py is project-local code that records the observed top-level verifier exit status. verify.py performs the actual Lean checks and source-integrity checks. The final manifest pins both execution scripts.
