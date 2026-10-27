# Komorebi Model-Theory Normalization v0.7

Canonical, modulus-bounded integer-preimage coordinates for the verified
observation-discovery algorithm. This is not a new p-adic version.

Read NORMALIZED_CORE.md, FORMALIZATION_COVERAGE.md, RESULTS.md,
PROOF_AUDIT_v07.md, DEVELOPMENT_FAILURES.md and CONTINUE_HERE.md.

## Integrity and Python replay

Use Python 3.10 or later. The port and checks need only the standard library.
Check distribution bytes BEFORE a replay, because the latter updates run records.

```sh
python tools/verify_integrity.py
python tools/validate_manifest.py LEAN_MANIFEST_v07.json --root .
python tools/validate_manifest.py COMPUTATION_MANIFEST_v07.json --root .
python v07_checks/audit_normalized.py
```

```python
import json
from pathlib import Path
from normalized_echelon import discover_normalized

source = json.loads(Path('certificates/scrambled_128bit.source.json').read_text())
tests, statistics = discover_normalized(source)
assert len(tests) == 2
print(statistics['final_basis'])
print(statistics['max_checkpoint_bits'])
```

This Python port is independently tested, NOT code extracted from the proof.
The verified executable is `normalizedPrimeDiscover` in NormalizedDiscovery.lean.
The full integer-preimage basis has d rows; it is not a minimum modular generating
family. The canonical key is relative to a fixed modulus, dimension, and ambient
column coordinates.

## Full Lean replay

Use the pinned runtime directory containing `toolchain/bin/lean` and
`workspace/.lake/packages/mathlib`:

- Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
- Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Work in a COPY. Preserve the recorded state before starting a new cold audit:

```sh
mv v07_evidence/COLD_STATE.json v07_evidence/COLD_STATE.distributed.json
python v07_checks/fresh_audit.py --runtime "$RUNTIME"
```

The fresh driver uses module-mode audit imports and at most 80 declarations per
axiom group. Each task records a checkpoint. To resume an interrupted active plan,
`python v07_checks/audit_lean.py --all` executes its remaining synchronous tasks.
A state marked FAILED must first be preserved and its actual failure addressed;
the saved recovery scripts document this release's specific interrupted attempts. A resumed task
checks the input, prior log, and build hashes. A missing prior build requires a new
cold run; it must not be treated as available from a historical path. Each Lean
process has a 90-second wall cap. Resource timeouts are failures/inconclusive,
never false mathematical conclusions. Upstream compiled Mathlib is reused.

The cold audit includes all 203 new kernel computations, proofs, axiom groups,
and positive/negative controls. `NormalizedCases/Case201.lean` and Case202 are
standalone duplicate convenience cases, not additional independent test sources.

## Boundaries

Stored integer basis entries are universally bounded by the modulus at normalized
queue boundaries. Temporary arithmetic values and total bit complexity remain
separate. No wall-time speedup, minimum formula size, learned discovery, verified
Python parser, or historical-novelty claim is made. The v0.6 original archive and
all its Lean proof bytes remain preserved; the current selected predecessor
dependencies are rebuilt, not every historical case suite.
