# Komorebi Logical Resolution v0.2

**Standard first-order translation, relational quotient contracts, and quantifier-sensitive resolution.**

This is a continuation of Logical Resolution v0.1, not a new p-adic block or a
replacement for Representation Calculus v0.4. The frozen v0.1 ZIP is in `history/`.
Its eight current Lean modules are reused byte-for-byte and rebuilt. Five new
modules complete the standard-syntax bridge and add a relational layer.

Start with `THEOREM_NOTE.md`, then `FORMALIZATION_COVERAGE.md` and `RESULTS.md`.
The accepted universal claims are the actual Lean declarations. Python examples
and finite counts are separate implementation audits. No novelty or independent
referee verdict is asserted.

## Reproduce

Python 3.11+ and the standard library suffice for the finite audit:

```sh
python tools/verify_integrity.py
python tools/audit_python.py
```

Distribution integrity must be checked BEFORE rerunning audits, which intentionally
replace current execution records. Prefer an extracted working copy.

For the complete strict Lean audit, provide the preserved runtime root containing
`toolchain/bin/lean` and `workspace/.lake/packages/mathlib` at the pins below:

```sh
python tools/run_checked.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python tools/validate_manifest.py LEAN_MANIFEST.json --root .
python tools/validate_manifest.py PYTHON_MANIFEST.json --root .
```

The wrapper cold-builds all 13 local modules, checks every named declaration's
axioms, and executes positive and expected-negative controls. It uses cached
pinned Mathlib dependencies, NOT a cold build of Mathlib. The multi-gigabyte
runtime/cache is deliberately not bundled.

Lean: `leanprover/lean4:v4.34.0-rc2`, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`.
Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
Source hashes and attribution: `source_records/MATHLIB_INPUT.json` and
`EXTERNAL_INPUTS.md`.

## Main results

* Constructive translation to actual Mathlib `FirstOrder.Language` formulas,
  with satisfaction and quantifier-rank preservation at every arity/nesting.
* A binary relation descends through an encoding iff it is constant on both fibers.
  Surjective operation/observation transports preserving AND reflecting the added
  relations preserve every translated formula, including nested quantifiers.
* Finite-rank two-sided witness matching implies truth agreement up to that rank.
* A three-vertex example agrees on all parameter-free one-variable standard
  quantifier-free formulas but is separated by `exists y, R(x,y)`. This query has
  no parameter-free quantifier-free replacement even within that one model.

The translated source fragment excludes state equality. The target library has
state equality, but our preservation theorem does not cover arbitrary formulas
using it. The special three-vertex quantifier-free counterexample DOES quantify
over all standard quantifier-free formulas, including state equality.

See `CONTINUE_HERE.md` for the next bounded target and exact remaining limitations.
