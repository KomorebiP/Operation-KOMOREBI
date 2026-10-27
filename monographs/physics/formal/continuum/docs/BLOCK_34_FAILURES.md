# Block 34 failure ledger

No failed attempt listed here is counted as proof evidence.

## Initial parent-cache build timeout

The first build of the checked v0.33 parent target reached the final three jobs
but exceeded the outer command window. The run is classified as inconclusive.
A resumed import-closure build completed successfully.

## Monolithic cumulative build timeouts

Three attempts to rebuild every cumulative top-level target progressed into the
terminal parent targets but did not emit terminal success receipts before the
outer execution limit. None is counted as a pass. The accepted mode is modular
cumulative verification: all 132 parent mathematical sources are compared
byte-for-byte with the frozen v0.33 ledger, and the complete 2,748-job Block 34
import closure is rebuilt and audited.

## First production verifier wrapper timeout

The initial all-in-one verifier completed the forced 2,748-job import-closure
build and the direct source/API compilations, but the outer wrapper expired
before the axiom and negative-control stages. It is not accepted as a complete
verification run. The final verifier reran every gate with the project
`LEAN_PATH` supplied directly to Lean and completed successfully.

## Sinusoidal witness elaboration repairs

The first non-affine witness draft contained three implementation-level issues:

- two constant-line continuity fields used a simplifier invocation that made no
  progress;
- the derivative of `A_y=sin x` in the `z` direction required explicit
  unfolding of the `z` shift;
- the trigonometric bound required the qualified theorem
  `Real.abs_cos_le_one`.

These were repaired before the successful warning-as-error compilation.

## Scope reduction retained deliberately

A sharper exact rectangular Stokes identity in terms of a surface integral of
`F` was considered but not inserted without a dedicated two-dimensional
integration theorem. Block 34 instead proves a fully checked derivative-sum
quadratic estimate. This is a conservative theorem-strength decision, not a
claim that the sharper identity is false.
