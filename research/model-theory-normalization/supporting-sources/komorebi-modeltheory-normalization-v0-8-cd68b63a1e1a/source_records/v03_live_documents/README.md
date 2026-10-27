# Komorebi Model-Theory Normalization v0.3

A checked bridge from discovered matrix representations to exact defining formulas
in Mathlib first-order logic. Start with `NORMALIZED_CORE.md`,
`FORMALIZATION_COVERAGE.md`, and `RESULTS.md`.

The two frozen predecessors are in `history/`; their hashes are in
`source_records/PREDECESSORS.json`. Relevant inherited proof and Python files are
copied unchanged. This is a model-theory release, not a new p-adic block.

## Python replay

Python 3.10 or later, standard library only, no package installation:

```sh
python tools/verify_integrity.py
python tests/audit.py
```

Run archive integrity before replaying tests: tests intentionally replace their
current result JSON and therefore change distribution hashes.

Export an untrusted Lean candidate plus its original-language logical formula:

```sh
python tools/export_discovery_logic.py certificates/scrambled_128bit.source.json \
  certificates/scrambled_128bit.certificate.json \
  --namespace MyExample --output /tmp/MyExample.lean
```

Export is not acceptance. The proof must subsequently compile against the included
library and pinned Lean/Mathlib environment.

## Complete formal replay

Use the saved Linux offline runtime (or a matching installation) with exact pins:
Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, and Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. On Windows the supplied runtime runs
under WSL. Runtime binaries and the multi-gigabyte upstream cache are not included.

```sh
python tools/audit_all.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --selection all --workers 3
python tools/validate_manifest.py LEAN_MANIFEST.json --root .
python tools/validate_manifest.py COMPUTATION_MANIFEST.json --root .
```

The `all` selection cold-rebuilds the 20 supporting modules and all 202 generated
instances. `--selection smoke` rebuilds the same supporting modules plus the large,
delayed, hidden-coordinate, and one zero-coordinate example. It is not a second
complete instance-suite check. Each command has a 90-second timeout. Every library
module is checked with warnings treated as errors. Independent generated modules
may compile concurrently, each with one Lean worker. The audit refuses a mismatched
runtime or changed copied predecessor input. It reuses, rather than rebuilds, the
pinned upstream Mathlib cache.

The provided scripts write auditable before/after hashes and reject unexpected
axioms, missing declaration audits, incorrect controls, and incomplete commands.

## Scope

Every initial state, deterministic unary operations, exact observation values, and
the declared observation language. Quantified target queries use the actual image,
not arbitrary points in a larger free coordinate array. The main equivalence formula
uses only state guards and the original operations/observations. Per-class formulas
also use the language's existing value names.

No full first-order elementarity, quantifier elimination, theory-wide elimination
of imaginaries, minimum-formula claim, learned policy, or held-out performance
advantage is asserted. Python parsing, discovery, checking and export are tested
programs, not formally verified executables.
