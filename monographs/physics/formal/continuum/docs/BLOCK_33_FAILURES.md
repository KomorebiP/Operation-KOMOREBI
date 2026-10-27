# Block 33 failure ledger

No failed attempt listed here is counted as proof evidence.

## Unsafe `Repr` derivation

The first draft derived `Repr` for structures containing `Real`. In the pinned
Lean environment this introduced an unsafe `Real.instRepr` dependency and led
to an invalid-declaration/compiler failure. All such derivations were removed.
The final mathematical source contains no `unsafe` declaration.

## Missing parent object files

An early direct compilation was attempted before the checked v0.32 import
closure had been restored. Lean reported missing parent object files. The
2,426-job parent closure was built with the pinned runtime, after which the new
module compiled normally. This was an environment ordering failure, not a
mathematical result.

## Proof elaboration repairs

Several initial expressions required repair:

- a Boolean child-coordinate identifier conflicted with Lean syntax;
- the cubical plaquette definitions required explicit unfolding;
- the dyadic square identity required an explicit power calculation;
- the direct operator theorem initially referenced a later local declaration.

Each issue was repaired and the resulting source was recompiled with warnings
as errors.

## Monolithic cumulative build timeout

A production attempt to rebuild every cumulative target progressed into the
terminal parent target set but exceeded the outer execution window before a
success receipt was emitted. It is classified as inconclusive and is not used
as verification evidence.

The accepted verification is modular cumulative verification: all 131 parent
mathematical sources are byte-identical to the checked v0.32 ledger, and the
complete 2,535-job Block 33 import closure, direct source, public API, axiom
audit, and negative controls pass under the pinned runtime.
