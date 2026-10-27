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

The unchanged accepted formal development contains 162 production modules and four import entrypoints. It has 1,859 explicit theorem or lemma declarations and 5,339 exported project declarations. The exported-declaration inventory additionally counts definitions and generated helpers.

All sixteen principal analytic theorem groups have formal counterparts. Chapter 30's actual infinite diagonal model, certified tails, sharp all-budget asymptotic, and rounded noisy rate are available through `KomorebiSpaceDiagonal`. That entrypoint also imports the explicit inexact-solver rate in `DiagonalInexactRate` and the concrete nonclosed-range and closure/nonattainment results in `DiagonalRangeObstruction`. Both modules contribute declarations to `KomorebiSpace.DiagonalRegularization`. The selected theorem map is in `../verification/LEAN_THEOREM_MAP.json`. Exact hypotheses are given by the declaration types.

The accepted integrated replay freshly compiled all 166 project targets, exported all 5,339 project declarations by module provenance, and checked their recursive axiom dependencies. All 56 controls had the specified outcomes: 18 acceptances, 35 elaboration rejections, and three axiom-policy rejections. The historical cumulative audit's 44 controls and the accepted diagonal completion's eight controls were rerun together with four added controls for the two concrete connections. See [the runner guide](../verification/runner/README.md) for the acceptance conditions and evidence files.

For an executable rational example linked to the general theorem statements, read [WORKED_EXAMPLE.md](../examples/WORKED_EXAMPLE.md). The example's Python verifier is not a certified extraction from Lean.

## Reproducibility

The required Lean version is `4.34.0-rc2`. The required mathlib revision is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Preserve the toolchain file and dependency manifest together.

The source package does not bundle the multi-gigabyte compiler and dependency cache. A matching local environment may be reused. For the complete current replay, run the command in [USAGE.md](USAGE.md). The accepted earlier diagonal evidence is preserved intact in `../verification/DIAGONAL_ACCEPTED_EVIDENCE.zip`. Its `REPRODUCIBILITY.md` documents that historical audit and the compatibility detail used on its verification host. The separate Technical Record preserves the parent and continuation histories.

The publication's citation is in [CITATION.bib](../CITATION.bib). Original software uses MIT and original writing uses CC BY 4.0, with third-party terms preserved. See [REUSE.md](../REUSE.md) and [LICENSE.md](../LICENSE.md) for the current grant and exact scope.
