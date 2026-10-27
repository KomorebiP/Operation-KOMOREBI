# Evidence validator provenance

validate_manifest.py was transcribed from the installed mathbox computation-audit skill's scripts/validate_manifest.py, read in full through the skill resource interface on 26 September 2026. Three explanatory comment lines in the software-version branch were omitted. Its schema and validation logic are retained. It is an evidence-record validator, not the Lean proof checker.

The inherited run_recorded.py and verify.py remain available for monolithic execution. The completed v0.6.0 run uses the project-local verify_staged.py, which invokes and records every compiler command, pins inputs before all batches, and requires full plan, audit and log-integrity checks at finalization. It imports theorem-enumeration and source-scan helpers from verify.py. The final manifest pins these two executed scripts. Its process record identifies a staged completion, not one uninterrupted process.
