# AVOC v0.25.0 — fresh verification record

## Result and census

PASS: **136/136** final local compilation targets; **1,310/1,310** exact-name theorem
axiom reports; **63/63** substantive expected negative rejections.

- 74 new theorem/lemma declarations in six modules.
- 123 non-audit AVOC modules; 19,935 non-audit source lines.
- All 117 inherited non-audit modules byte-identical to v0.24.
- Baseline ZIP SHA256:
  `77c1e519d8d464cc52a7333f7f375110da0aded9f5bc09140b29217c0eb989ea`.
- Baseline CRC and its 5,670 original payload hashes passed before modification.

Counts include helpers/examples, not independent discoveries.

## Runtime and scope

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d. Mathlib
 aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine external revision checks passed.
Python 3.13.5; SQLite 3.46.1; Linux x86-64.

The offline archive assembly verified all seven part CRC/SHA values and the complete
compressed archive hash. An extraction interruption was followed by a complete fresh
extraction. No separate full-byte comparison of the extracted runtime is claimed.

The LOCAL build directory began empty. Inherited local modules were compiled, and the
final versions of changed modules and their descendants were then compiled. Every
final record has current source/output/log/direct-import hashes, return code zero,
no timeout and unchanged source/imports during that compilation. This is not a fresh
source rebuild of mathlib, compiler verification or an independent kernel.

## Axiom audit and source check

FullAudit names exactly the 1,310 inventoried declarations. The union of dependencies is:

```
propext
Classical.choice
Quot.sound
```

No placeholders, project-defined axioms, native_decide or unsafe theorem-like positive
source declarations were found. The independent comment-aware declaration census
matches the inventory. All positive compilation targets use warnings as errors.

## New negative files

- FalseGeneratedSemantics: tries to identify AND with OR despite a checked witness.
- FalseFreeSynthesis: contradicts the proved nonzero charged search example.
- FalseSynthesisAlwaysImproves: contradicts zero-credit retention of the reference.
- FalseSmallerProgramProfitable: contradicts the checked negative-net campaign.

All 63 files reject substantively, not because of missing modules or timeout. A failed
proof script alone is not used as a proof of negation; positive sources establish the
relevant obstructions.

## Independent exact implementation comparisons

Final tests used an independent Python bitset semantics (all eight Boolean assignments),
explicit product grammar and separate candidate-selection/cost oracle. Actual requests
were sent to the executed Lean entrypoint.

- 747 campaign comparisons across depth 0/1 and named depth-2 targets, multiple trial
  limits, insufficient/adequate credits and call counts;
- 255 direct equivalence comparisons;
- 5,976 individual input/output/visit checks, eight for each campaign;
- ten invalid wire requests rejected;
- sixteen protected file/SQLite/Lean-process scenarios passed.

The live scenarios include generated AST persistence and invocation after reopening,
negative campaign net, three-flag synthesis, retained pre-search reservation, interrupted
search without result dispatch, transactional rollback, lost post-commit response,
changed records/charges/objective, cooperative locking and invalid configurations.

These interruption fixtures use controlled Python exceptions and transaction rollback.
They are not process-kill or power-loss experiments. Older live filesystem, recovery and
retry suites were not rerun and remain historical.

Final test provenance:
- differential: started 2026-09-13T18:01:27.835345+00:00; 9.53684 seconds;
- live: started 2026-09-13T18:01:38.273972+00:00; 14.38095 seconds.

Those times are this host's test-execution measurements, not asymptotic bounds or
production performance. Exact timestamps/runtimes are retained in the JSON records.
Input-source hashes match before/after and the final checkout. The evidence collector
independently rereads every retained campaign answer and reruns its Python oracle.

## Fresh command-line confirmation

After final test collection, the documented `run` and `invoke` commands were executed
in a new `results/v0.25.0/final_cli_demo/` store. Both returned the generated pair
conjunction, 85 tested entries, total charge 6,971 and net 23,029. The retained
`final_cli_search.json` and `final_cli_invoke.json` record those actual commands.

## Evidence locations

`results/v0.25.0/summary.json`, `declaration_inventory.json`, `new_declarations.json`,
`build_order.json`, per-target clean logs/JSON, `full_axiom_audit.*`, negative records,
`differential_provenance.json`, `live_provenance.json`, oracle requests/outputs, and demo
JSONs. `AUDIT.json` duplicates the summary at project root.

Payload and ZIP checks are additional packaging checks, not replacements for theorem
or implementation checks. The source ZIP excludes all runtime/dependency binaries.
