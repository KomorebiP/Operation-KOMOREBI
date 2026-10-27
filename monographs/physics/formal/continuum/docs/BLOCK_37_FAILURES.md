# Block 37 failure ledger

## Excluded runtime smoke test

A cold `import Mathlib` smoke test read hundreds of gigabytes of logical overlay data and did not terminate within the operational window. It was stopped and is not verification evidence. The targeted project build subsequently compiled normally.

## Initial source errors

The first draft failed at:

- the preimage-of-singleton proof for the finite measurable equivalence;
- an equality orientation in the singleton-mass calculation;
- the definitional identification of the digitwise infinite-product map.

These were repaired by explicit inverse transport, equality symmetry, and a typed function-extensionality lemma.

## Binary-coordinate extension errors

The first binary-coordinate draft misapplied `Real.ofDigits_SurjOn` and did not unfold the subtype coercion in the noninjectivity proof. Both proof terms were corrected before the accepted build.

## Cumulative build timeout

The first full cumulative build was externally stopped after substantial progress and did not emit a terminal success receipt. It is classified as inconclusive. The build was resumed on the same exact source tree and later emitted terminal success for 3,930 jobs.

## Deliberate boundary

A Lebesgue pushforward theorem was not inserted as an assumption. Continuity, surjectivity, and quotient-map status do not by themselves prove measure preservation.
