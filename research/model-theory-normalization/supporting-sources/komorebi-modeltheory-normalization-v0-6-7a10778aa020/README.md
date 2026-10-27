# Komorebi Model-Theory Normalization v0.6

Verified executable incremental INTEGER ECHELON membership, exact modular preimages,
a cached FIFO discovery algorithm and its original-language logical definition.
The new Lean solver has no untrusted proposer, membership certificate input or
exhaustive coefficient-enumeration fallback. It is not a canonical Smith solver.

Read `NORMALIZED_CORE.md`, `FORMALIZATION_COVERAGE.md`, `RESULTS.md`,
`PROOF_AUDIT_v06.md`, `DEVELOPMENT_FAILURES.md` and `CONTINUE_HERE.md`.
The full immutable v0.5 predecessor is retained under `history/`.
The parallel Representation Calculus and p-adic branches are not renumbered.

## Integrity and finite execution

Python 3.10+; standard library only. Check distribution integrity BEFORE rerunning
an audit: audit results contain fresh times and intentionally rewrite current records.

```sh
python tools/verify_integrity.py
python tools/validate_manifest.py LEAN_MANIFEST_v06.json --root .
python tools/validate_manifest.py COMPUTATION_MANIFEST_v06.json --root .
python v06_checks/audit_echelon.py
```

A convenient Python port is included, separately from the verified Lean executable:

```python
import json
from pathlib import Path
from integer_echelon import discover_echelon

source = json.loads(Path('certificates/scrambled_128bit.source.json').read_text())
tests, statistics = discover_echelon(source)
assert len(tests) == 2
print(tests)
print(statistics)
```

This port is independently tested, NOT proved to be equivalent code extraction.
The actual verified algorithm is `fastPrimeDiscover` in `EchelonDiscovery.lean`.

## Lean reproduction

The pinned runtime is Lean 4.34.0-rc2, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, with Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
Set RUNTIME to a directory containing `toolchain/bin/lean` and
`workspace/.lake/packages/mathlib`. Runtime and cache bytes are intentionally not
bundled. Source and binary pins are in `v06_evidence/ENVIRONMENT.json`.

A selected independent cold replay can be run without changing distributed audit
records. Use a NEW external state path:

```sh
python v06_checks/replay_selected.py --runtime "$RUNTIME" --state /tmp/repr06-replay.json --init
python v06_checks/replay_selected.py --state /tmp/repr06-replay.json --batch 2
# Repeat the batch call until all planned tasks complete, then:
python v06_checks/replay_selected.py --state /tmp/repr06-replay.json --finish
```

This selected replay rebuilds the generic dependency chain, concrete boundary
examples, standalone large and stress computations, and all eight controls.
It does not claim to rebuild all 203 cases a second time.

For a FULL rerun, use a working copy, preserve the distributed state records first,
and follow the bounded stages:

```sh
python -c "from pathlib import Path; import time; r=Path('v06_evidence'); [(r/n).rename(r/(n+'.saved.'+str(time.time_ns()))) for n in ('COLD_STATE.json','AXIOM_GROUP_STATE.json') if (r/n).exists()]"
python v06_checks/audit_lean.py --runtime "$RUNTIME" --init
python v06_checks/audit_lean.py --batch 3
# Repeat until exactly 39 build tasks are complete. Do not start the monolithic
# axiom task on a resource-constrained machine. Instead:
python v06_checks/audit_axiom_groups.py --init
python v06_checks/audit_axiom_groups.py --one
# Repeat --one until all eight groups complete; then run the eight controls:
python v06_checks/audit_lean.py --batch 1
# Repeat until TASKS_COMPLETE, then:
python v06_checks/audit_lean.py --finish
python v06_checks/finalize_records.py
```

Every resumed batch verifies accepted inputs and completed artifacts. Expired or
missing build artifacts require a new cold run; an old IN_PROGRESS record is not
proof that a process is still running. No PASS is written for incomplete work.

The all-case computations are in `formalization/EchelonComputed00.lean` through
`EchelonComputed16.lean`. Standalone copies are under `formalization/EchelonCases`.
The copies do not count as additional verified research results.

## Limits

The representation has d full integer basis rows, not necessarily the minimum
number of modular generators. Tail coefficients are not canonically reduced;
bit complexity and coefficient growth require further work. The mathematical
source contract is all-state unary linear dynamics and observational logic.
No arbitrary logical-invention theorem, learned proposer, held-out performance
claim, historical novelty or independent referee approval is asserted.
