# Komorebi Model-Theory Normalization v0.5

Verified membership-witness checking, executable complete-trace replay, a guarded
correct oracle, and a bounded-width untrusted Smith proposer.

Start with `NORMALIZED_CORE.md`, `FORMALIZATION_COVERAGE.md`, `RESULTS.md`,
`PROOF_AUDIT.md` and `CONTINUE_HERE.md`. The immediate v0.4 archive is frozen under
`history/`; it contains the previous complete provenance chain. This version does
not renumber the parallel Representation Calculus or p-adic projects.

## Independent Python reproduction

Python 3.10+; standard library only. Run distribution integrity BEFORE rerunning
checks, because evidence records contain fresh timestamps and will be rewritten.

```sh
python tools/verify_integrity.py
python tools/validate_manifest.py LEAN_MANIFEST_v05.json --root .
python tools/validate_manifest.py COMPUTATION_MANIFEST_v05.json --root .
python v05_checks/audit_backend.py
```

`certified_backend.certified_discover(source)` returns a complete trace and working-
width statistics. Independently call `new_checks.check_trace.check_trace(source,
trace)` before using it. The checker receives the intended source separately.

To emit a new kernel-checkable data instance:

```sh
python v05_checks/export_checked_data.py source.json trace.json MyExample MyExample.lean
```

The exporter itself is unverified. Lean must accept the emitted source. It contains
finite source matrices and evidence data, one executable replay equation, and its
universal reference-output, all-word and standard-formula consequences.

## Lean reproduction

The pinned runtime is Lean 4.34.0-rc2 with Mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Set RUNTIME to the restored directory
containing `toolchain/bin/lean` and `workspace/.lake/packages/mathlib`. Runtime/cache
bytes are intentionally excluded. Exact pins are in `v05_evidence/ENVIRONMENT.json`.

Preserve the distributed completed audit state under a new name before starting:

```sh
python -c "from pathlib import Path; import time; p=Path('v05_evidence/COLD_STATE.json'); p.rename(p.with_name('ARCHIVED_COLD_STATE_'+str(time.time_ns())+'.json'))"
python v05_checks/audit_lean.py --runtime "$RUNTIME" --init
python v05_checks/audit_lean.py --batch 2
# Repeat --batch 2 until TASKS_COMPLETE, then:
python v05_checks/audit_lean.py --finish
python v05_checks/finalize_records.py
```

The complete audit has 39 local builds, one axiom audit and seven controls: 47 tasks.
Each batch is synchronous and verifies accepted inputs and completed artifacts.
No PASS is written for a partial run. An expired external build cannot be resumed
just because an old state file says IN_PROGRESS; preserve that record and restart.

Regenerating the two v05 manifests after a rerun is separate from the distribution
FILE_MANIFEST.json, which records the original delivered bytes.

## Scope

The executable Lean validator is proved sound. Every one of the 203 saved optimized
producer traces is kernel-checked as DATA, without state enumeration. The producer
and Smith routine remain unverified programs. The guarded fallback is correct but
can be expensive. The no-fallback complete-trace checker rejects missing/invalid
work; it does not interpret such a failure as proof of nonexistence.

The discovered list is not necessarily a minimal list of tests. The stress example
has 24 accepted raw tests and a final row module with one generator. Higher model-
theoretic expressivity and arbitrary relational queries have separate contracts.
