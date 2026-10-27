# Komorebi Lean Verification — verified tranche v0.2.0

Author: Komorebi P.

This Lean 4/Mathlib project kernel-checks a restricted finite projector-calculus
tranche.  It is deliberately narrower than the surrounding research corpus:
the build establishes the declarations in this repository, not every item in
the source claim ledger and not the program's broader universality claims.

## What is checked

- `ProjectorCore.lean` is the byte-identical browser-safe core v1.2.2 recovered
  from the prior workspace.  Its 39 theorem declarations compile unchanged.
- `ExactCoordinates.lean` defines the packet space independently as
  `∀ i, LinearMap.range (P.proj i)` and proves analysis and finite-sum synthesis
  are inverse linear maps.  Thus a complete orthogonal projector family gives
  an exact linear equivalence with its range-restricted packet coordinates.
- `FibreRefinement.lean` upgrades pointwise fibre masks to linear projectors and
  proves that a coarse fibre mask is exactly the sum of the independently
  defined fine masks mapping to it.
- `ResidueProjectors.lean` specializes that law to coefficient sequences:
  every projector modulo `N` is the exact sum of the compatible projectors
  modulo `N * M`, for positive `N` and `M`.
- `KernelAudit.lean` instantiates the results on four rational coordinates,
  tests parity refinement and sixteen-block operator reconstruction, and runs
  `#print axioms` on the principal declarations.
- The legacy core additionally checks transfer-block reconstruction and
  composition, transitive matrix-support closure, the geometric weighted
  finite-difference formula, and polyphase coefficient-section composition.

## Reproduce the checks

With a conventional Elan installation:

```bash
lake exe cache get
lake build
lake env lean KomorebiVerification/KernelAudit.lean
```

In the supplied container workspace, first load its compatibility environment:

```bash
source ../lean-runtime/lean-env.sh
lake build
lake env lean KomorebiVerification/KernelAudit.lean
```

The project pins Lean in `lean-toolchain` and the exact Mathlib dependency graph
in `lake-manifest.json`.

## Trust and scope boundary

There are no project-specific axiom declarations, theorem placeholders, or
unsafe declarations in the checked tranche.  `#print axioms` reports only
Lean/Mathlib's standard foundations as applicable: `propext`,
`Classical.choice`, and `Quot.sound`; it reports no `sorryAx`.

Some legacy abstract reconstruction statements follow from the `complete`
field of `LinearProjectorFamily`.  The range-restricted reverse coordinate law
is stronger: it genuinely uses idempotence and pairwise orthogonality.  The
concrete fibre theorems derive idempotence, orthogonality, completeness, and
refinement from pointwise masks rather than assuming those conclusions.

This release does **not** kernel-check all 594 catalogue records or all files
mentioned in the earlier 60-file release audit.  Numerical regression counts,
metadata marked `kernelChecked`, manuscript labels such as “proved
internally,” and historical-novelty claims are not substitutes for Lean kernel
acceptance.
