# Komorebi Lean Verification — Paper I v1.0.1

Author: Komorebi P.  
Verification date: 2026-09-03  
Manuscript release: *Projector-Resolved Seed Calculus I*, v1.2.1

This Lean 4/Mathlib component is theorem-complete for the revised,
certificate-explicit 35-row Paper I completion contract. “Theorem-complete”
means that every revised contract row has an exact or stronger compiled Lean
declaration at the scope recorded in
[`LEAN_THEOREM_MAP_v1.0.1.md`](LEAN_THEOREM_MAP_v1.0.1.md). It does not mean
that Lean constructs the classical decomposition or spectral certificates
consumed by several rows.

## Completion modules

Component v1.0.1 adds literal quotient-evaluation glue for rows 1 and 2,
complete direct axiom reporting for all 84 mapped declarations, an executable
map checker, and a namespace-wide fail-closed trust audit. The mathematical
completion modules introduced in v1.0.0 remain the basis of the 35-row scope.

The six modules added for component v1.0.0 are:

- `SeedRankOperations.lean`: free presentations, unrestricted cardinal cyclicity,
  semilinear quotient monotonicity, image-algebra invariance, shared and
  independent product formulas, the algebraic tensor-product bound, and the
  scalar-quotient obstruction (contract rows 2–9).
- `SemisimpleCompletion.lean`: the finite split-product maximum formula, the
  full-matrix natural-module result, and the multiplicity obstruction from
  supplied algebra and compatible module equivalences (rows 10–12).
- `SingleOperatorGraph.lean`: certificate-explicit single-operator and cyclic
  matrix criteria, operator-algebra rank bridges, certified diagonalizable
  graph rank, and unconditional path and complex-cycle results (rows 13, 14,
  and 32).
- `PacketNaturalityCompletion.lean`: packetwise equality, finite packet powers,
  the dependent full block algebra, dimension formulas, sharp algebraic
  support converses, reachability, conjugacy invariance, strict naturality,
  and the typed quiver certificate (rows 16, 21, 23–28, and 30, together with
  the algebraic part of row 26).
- `TopologicalCompletion.lean`: dense-isometric Banach completion, the finite
  bounded-projector packet equivalence, arbitrary bounded-idempotent range
  closure and its packet-family specialization, adjoint reversal,
  topological reachability obstruction, dense bounded realization, and the
  concrete bilateral-shift minimum-one theorem (topological parts of rows 1,
  17, 18, 22, 26, 29, and 31).
- `EllipticAlgorithms.lean`: algebraic coordinate identities for the affine
  cubic model and mathematical termination/correctness specifications for
  orbit hulls, transfer-block tables, and the certificate-driven exact graph
  seed-rank computation (rows 33–35 for the algorithms).

The earlier modules remain part of the checked dependency graph. They provide
the projector foundation, exact packet coordinates, fibre and residue
refinement, block transport and reconstruction, cardinal seed-rank basics,
the one-block semisimple calculation, full-matrix cyclicity, and path Krylov
certificates.

## Reproduce the checks

With Elan available:

```bash
lake exe cache get
lake --wfail build
python scripts/verify_theorem_map.py
lake env lean -E warning KomorebiVerification/KernelAudit.lean
```

The project pins the Lean toolchain in `lean-toolchain` and the exact Mathlib
dependency graph in `lake-manifest.json`. The warning-fatal public aggregate
build completed all 8,883 jobs successfully. The audit is deliberately
standalone so importing `KomorebiVerification` has no diagnostic side effects.

## Trust and scope boundary

There are no project-specific axiom declarations, explicit opaque constants,
theorem placeholders, or unsafe declarations in this checked component. The
map checker enforces exactly 35 rows, 84 unique compiled declarations, and 84
matching direct `#print axioms` reports. The fail-closed audit traverses 1,126
compiled project declarations. It reports only Lean/Mathlib's standard
foundations as applicable: `propext`, `Classical.choice`, and `Quot.sound`; it
reports no `sorryAx`.

The following are deliberately outside the completion claim:

- construction of Wedderburn–Artin, Jordan/primary, eigenbasis, polynomial,
  quotient, or exact spectral certificates from bare hypotheses;
- a verified eigensolver, symbolic factorization routine, extracted executable
  implementation, complexity analysis, benchmark, or performance guarantee;
- projective smoothness, genus, or a geometric discriminant theorem for the
  elliptic example;
- infinite packet expansions, unbounded-operator variants, completed tensor
  products, historical-priority claims, or broader universality claims.

Rows 13, 14, 32, and 35 are therefore explicitly conditional on the
certificates itemized in the theorem map. The algorithm declarations verify
mathematical specifications; they do not claim executable certificate
construction.
