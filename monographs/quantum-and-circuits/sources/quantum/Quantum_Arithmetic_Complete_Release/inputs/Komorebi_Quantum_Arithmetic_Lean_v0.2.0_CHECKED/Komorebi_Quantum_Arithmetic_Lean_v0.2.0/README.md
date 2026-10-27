# Arithmetic Becomes Interference

## Komorebi quantum arithmetic bridge, version 0.2.0

This package formalizes the finite q = 12 worked example accompanying
*Mathematics Between Minds*. It preserves every theorem statement and every
coefficient table from the 0.1.0 draft.

The active sources use no proof placeholders, custom axioms, or native decision
tactic. Concrete certificates use direct kernel reduction. Symbolic semantic
lemmas use ordinary Lean proof terms.

## Sources

* `QuantumArithmeticBridge.lean` contains all 22 original theorem statements.
* `QuantumArithmeticSpecification.lean` connects the literal tables to coprimality,
  exact root order, cyclic convolution, orthogonality, and actual probability tables.
* `QuantumArithmeticComplex.lean` proves that the rational coordinate calculations
  have their stated complex arithmetic and Fourier meaning.
* `QuantumArithmeticUnitary.lean` proves character orthogonality and both unitary
  matrix identities for the normalized twelve dimensional Fourier matrix.
* `AxiomAudit.lean` prints the dependencies of every theorem.

See `THEOREM_INDEX.md`, `PROOF_BOUNDARY.md`, and `verification/final_run/VERIFICATION.json`
for exact scope and the recorded outcome. Historical failed scripts are preserved
under `history` and are not part of the active build.

## Reproduce with the existing portable kit

Run under Linux x86-64 or WSL2 with Python 3:

```sh
python scripts/verify_lean.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The runner uses a fresh source directory, compiles all four modules with warnings
as errors, audits every theorem, replays each module with `leanchecker`, rejects
four deliberate mutations of the source, and reruns the exact Python verifier.
It makes no network requests. Any timeout or unexpected compiler error fails the
run. Negative controls do not count as successful merely because a command failed.

The required pinned versions are recorded in `lean-toolchain`, `lakefile.toml`,
and `lake-manifest.json`. A normal writable Mathlib installation using these pins
can build the four libraries with `lake build`. The full verification runner above
is the route exercised for this release.

The compiler and Mathlib runtime are not duplicated in this source archive.
`RESTORE_RUNTIME.md` identifies the existing portable archives and records the
assembly hash used in this session.

## Interpretation

This is a formalization of the example, not a claim of a new Ramanujan identity,
a proof for arbitrary modulus, a quantum speedup, or a hardware experiment.
The philosophical essay itself has not been turned into a formal theorem.
