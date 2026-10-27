# Komorebi Logical Resolution v0.1

**First model-theory bridge: observational formulas, exact quotients, and definability boundaries.**

This is a new branch based on two unchanged semantic modules from Representation
Calculus v0.4. It is not Representation Calculus v0.5, p-adic Block 16, a replacement
for the full corpus, or a claim that general model theory has been formalized.

## Verified scope

The six new Lean modules define a well-scoped observational first-order fragment,
prove its exact relation to behavior, preserve its quantified formulas through
surjective exact transports, compile finite sufficient tests into defining formulas,
and prove explicit finite/infinite limits of the construction.

The final cold run checks eight library modules (two inherited, six new), 73 named
theorem declarations (50 new), and 132 named declarations altogether. Only the
standard dependencies `propext`, `Classical.choice`, and `Quot.sound` occur. All
accepted sources pass warnings-as-errors. Two false-claim controls and a deliberately
unproved placeholder are rejected. A positive control is accepted.

The exact finite Python reference audit passes 38,077 check calls over 28 systems.
It is not a verified executable or an AI-discovery benchmark. The universal claims
are in the Lean statements, not extrapolations from the finite tests.

## Read first

- `THEOREM_NOTE.md`: precise mathematical statements, proofs, and interpretation.
- `FORMALIZATION_COVERAGE.md`: what is and is not checked.
- `PROOF_AUDIT.md`: separate authoring-assistant semantic self-review.
- `RESULTS.md`: actual execution results and limits.
- `CONTINUE_HERE.md`: one bounded next target.
- `source_records/LINEAGE.json`: exact parent archive and unchanged file hashes.

## Reproduce

Use Lean `leanprover/lean4:v4.34.0-rc2` (commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`) and its matching Std library.
No Mathlib or Python packages are required. Python 3.10 or newer is intended;
this release was executed with Python 3.13.5.

First check the delivered bytes, before rerunning scripts that intentionally rewrite
current execution evidence:

```sh
python tools/verify_integrity.py
python tools/run_checked.py --lean /absolute/path/to/toolchain/bin/lean
```

Or run each audit separately:

```sh
python tools/audit_python.py
python tools/verify_lean.py --lean /absolute/path/to/toolchain/bin/lean
```

The full wrapper produces `LEAN_MANIFEST.json` and `PYTHON_MANIFEST.json`, validated
against their actual input/output hashes. Per-module Lean timeout is 60 seconds;
an enclosing audit has a 180-second cap. Timeouts never count as proof success.

No commands continue after this interaction. No binary toolchain or font files
are distributed. `tools/restore_core.py` documents the restoration used in this
container; it is not needed when a matching Lean installation is already available.

## Essential restriction

Observation-value equality is allowed. Equality of states is deliberately absent.
All values are available as named literals; quantifiers range over states. The
value domain and its literals are fixed under transport. This is a checked fragment,
not an elementary embedding theorem for an unrestricted first-order language.
