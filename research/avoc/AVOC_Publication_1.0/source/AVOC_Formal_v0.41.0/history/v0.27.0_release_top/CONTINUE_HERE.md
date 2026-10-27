# Continue from AVOC v0.27.0

Read README.md, PROOF_BOUNDARY.md, FORMAL_THEORY.md, GAP_LEDGER.md and results/VERIFICATION_v0.27.0.md. Check SHA256SUMS.txt before changing files.

Baseline: semantic-feedback v0.26 only, 1,393 inherited + 54 new = 1,447 declarations. No merge with the alternate rewrite-transfer branch. All prior non-audit baseline modules are preserved byte-identically.

Main new symbols:
- CostCertificate.lower_bound / witness_global_minimum / exact_cost_unique
- BoolClosure.check_bank_parts / query_globally_minimum / query_cost_fixed
- SemanticLibrary.paid_query_certified / import_many_accounting / stop_if_cost_covers_all_saving
- LibraryCodec.load_accepted_source / loaded_query_global

Actual executable certificate: examples/library/global.json, 256 rows, 1,640 total nodes, max 10, 196,869 closure obligations. It matches examples/library/lean_depth3.json exported from a fresh inherited Lean generator run. Validate and publish using tools/global_library.py; every reopened query revalidates, without generation.

Do not convert the unsuccessful optional monolithic static-table kernel reduction into a pass. Generic theorem soundness and executed certificate acceptance passed; that one proof attempt timed out after 30 seconds. No native-evaluation axiom bypass was used.

The next task should be driven by a new workload or cost question, not another proof of bounded Bool3 search. Prefer the generic algebra/certificate interface plus a meaningful typed domain, or costed selective reuse. Preserve all host, runtime, IO, certificate and tariff boundaries. New proof/test runs must use fresh evidence; old logs are historical.
