# Komorebi Model-Theory Normalization v0.8

Start with NORMALIZED_CORE.md, FORMALIZATION_COVERAGE.md and RESULTS.md.
The new result is verified bounded temporary coefficient arithmetic for the
canonical integer-lattice discovery backend. COST_MODEL.md clearly separates the
written bit-operation analysis from the actual Lean peak and Euclidean-call theorems.

## Python port

Python 3.10 or later; no third-party package is needed for the new finite audit.

```sh
python v08_checks/verify_integrity.py
python tools/validate_manifest.py LEAN_MANIFEST.json --root .
python tools/validate_manifest.py COMPUTATION_MANIFEST.json --root .
python v08_checks/audit_python.py
```

Check distribution integrity and archived evidence BEFORE rerunning audits, since
fresh result timestamps/hashes intentionally differ. The port is separately tested,
not formally verified code extraction.

```python
import json
from pathlib import Path
from bounded_echelon import discover_bounded
source = json.loads(Path('certificates/scrambled_128bit.source.json').read_text())
tests, stats = discover_bounded(source)
print(tests)
print(stats['proved_bit_budget'], stats['arithmetic_peak'].bit_length())
```

Find the retained large source path in `v06_evidence/EXPORTED_DATA.json`, index 201;
that record is authoritative if the example filename above differs in an inherited
snapshot. Both the matrices and result are also literal in BoundedCase201.lean.

## Lean

The source requires Lean 4.34.0-rc2 (commit recorded in lean-toolchain and evidence)
and Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The large portable
runtime and compiled upstream cache are NOT bundled. With the restored project
runtime layout, a portable fresh local rebuild is:

```sh
python v08_checks/recheck_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --output /tmp/komorebi_v08_replay.json
```

It rebuilds the 49 selected local modules, all 203 computations, the axiom drivers
and controls using the pinned upstream cache. It does not rebuild all Mathlib.

`v08_checks/audit_lean.py` preserves the exact original execution protocol, including
its /mnt/data/model08_work temporary-directory convention. Its archived cold-state
paths are historical provenance, not promises that those temporary files exist on
a different computer. The portable recheck driver uses a new temporary directory.

## Provenance

The immutable immediate v0.7 archive is under history/. Its recursively contained
archives retain earlier checkpoints. Current inherited Lean/Python sources are
byte-identical; v08_evidence/PARENT_PRESERVATION.json lists the comparisons.
Old versioned evidence belongs to its original release; only v08_evidence and
results_v08 describe this run. There is no blanket fresh verification of the
entire historical corpus.
