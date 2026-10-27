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

The parent v1.13.0 publication contains 153 production modules and three import entrypoints. This continuation adds seven production modules and the `KomorebiSpaceDiagonal` entrypoint. It completes the actual infinite diagonal regularization family and tail estimates, the sharp budget asymptotic, and the rounded noisy parameter rate from Chapter 30.

All 273 exported declarations attributed to the new modules, including generated helpers, pass the recursive axiom-policy check. The independent statement audits and the final strict source replay are recorded in `../records/` and `../audit/`. The targeted controls for this continuation are separate from the parent's historical 44-control audit.

See `../README.md` for the exact three theorem interfaces and `../records/COMPLETION.json` for the final evidence map. The Lean source gives every hypothesis and conclusion.

## Reproducibility

The required Lean version is `4.34.0-rc2`. The required mathlib revision is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Preserve the toolchain file and dependency manifest together.

The source package does not bundle the multi-gigabyte compiler and dependency cache. A matching local environment may be reused. This package preserves the new verification commands, source identities, declaration inventory, control outcomes, and independent reviews. See `../REPRODUCIBILITY.md` for normal-host instructions and the compatibility detail required by this execution host.
