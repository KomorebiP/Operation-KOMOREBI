# Komorebi Space

A Lean library for coherent realizations, constrained correction, obstruction, descent, and quantitative repair.

The formal development builds coherent objects from compatible observations and studies which defects can be removed while preserving designated information. It includes categorical descent, normed repair, Hilbert minimum corrections, attained budget profiles, sharp dual certificates, regularization limits, and coordinate invariant stopping certificates.

The accompanying monograph develops the mathematics. The Lean guide explains the formal interfaces and maps mathematical statements to exact declarations.

## Use the library

From this directory, with the pinned Lean toolchain and dependencies available:

```sh
lake build
```

The configured default targets are `KomorebiSpaceCombined` and `KomorebiSpaceDiagonal`. A Lean file can import the complete development with

```lean
import KomorebiSpaceCombined
import KomorebiSpaceDiagonal
```

For smaller applications, import a specific module such as `KomorebiSpace.Correction`, `KomorebiSpace.BudgetDuality`, or `KomorebiSpace.CoordinateCovector`.

See `USAGE.md` for the environment, import entrypoints, inspection commands, and the distinction between a normal build and the full verification audit.

## Formal coverage

This edition contains 160 production modules and four import entrypoints. It has 1,846 explicit theorem or lemma declarations and 5,321 exported project declarations. The latter count includes definitions and generated helpers.

All sixteen principal analytic theorem groups have checked formal counterparts. Chapter 30's actual infinite diagonal model, certified tails, sharp all-budget asymptotic, and rounded noisy rate are available through `KomorebiSpaceDiagonal`. The selected theorem map is in `../verification/LEAN_THEOREM_MAP.json`. Exact hypotheses are given by the declaration types.

The parent verification and diagonal completion have distinct evidence records. The parent audit contains 44 controls; the diagonal completion contains eight additional targeted controls and a recursive axiom audit of all 273 new exported declarations. The edition verification records the integrated build and exact source hashes. See `../verification/README.md`.

## Reproducibility

The required Lean version is `4.34.0-rc2`. The required mathlib revision is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Preserve the toolchain file and dependency manifest together.

The source package does not bundle the multi-gigabyte compiler and dependency cache. A matching local environment may be reused. The accepted diagonal evidence is preserved intact in `../verification/DIAGONAL_ACCEPTED_EVIDENCE.zip`. Its `REPRODUCIBILITY.md` gives the strict replay instructions and the compatibility detail used on the verification host. The separate Technical Record preserves the complete parent and continuation histories.
