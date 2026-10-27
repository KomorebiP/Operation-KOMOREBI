# Komorebi Space

A Lean library for coherent realizations, constrained correction, obstruction, descent, and quantitative repair.

The formal development builds coherent objects from compatible observations and studies which defects can be removed while preserving designated information. It includes categorical descent, normed repair, Hilbert minimum corrections, attained budget profiles, sharp dual certificates, regularization limits, and coordinate invariant stopping certificates.

The accompanying monograph develops the mathematics. The Lean guide explains the formal interfaces and maps mathematical statements to exact declarations.

## Use the library

From this directory, with the pinned Lean toolchain and dependencies available:

```sh
lake build
```

The configured default target is `KomorebiSpaceCombined`. A Lean file can import the complete development with

```lean
import KomorebiSpaceCombined
```

For smaller applications, import a specific module such as `KomorebiSpace.Correction`, `KomorebiSpace.BudgetDuality`, or `KomorebiSpace.CoordinateCovector`.

See `USAGE.md` for the environment, import entrypoints, inspection commands, and the distinction between a normal build and the full verification audit.

## Formal coverage

The accepted source set contains 153 production modules and three import entrypoints, with 1,693 explicit theorem and lemma declarations. Its 5,048 exported project declarations also include definitions, instances, structure operations, and compiler generated helpers. The accepted audit includes 44 diagnostic controls and an axiom dependency check.

The general theorems described in the Lean guide are formalized. Three explicit analyses in the monograph have written proofs without a completed Lean translation in this edition: the infinite diagonal regularization family and tail estimates, the sharp asymptotic budget comparison, and the rounded noisy parameter rate. These are formal coverage boundaries, not unproved mathematical claims in the monograph.

`../verification/LEAN_THEOREM_MAP.json` provides a selected reference to declarations discussed in the guide. The Lean source gives every exact hypothesis and conclusion.

## Reproducibility

The required Lean version is `4.34.0-rc2`. The required mathlib revision is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Preserve the toolchain file and dependency manifest together.

The source package does not bundle the multi-gigabyte compiler and dependency cache. A matching local environment may be reused. The separate technical record preserves the accepted verification commands, source identities, declaration inventory, control outcomes, and independent reviews.
