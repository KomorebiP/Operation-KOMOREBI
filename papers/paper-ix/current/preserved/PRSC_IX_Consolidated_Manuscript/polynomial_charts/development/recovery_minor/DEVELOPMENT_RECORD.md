# Recovered minor-selection proof

Author: Komorebi P.

This source was reconstructed after workspace maintenance removed the earlier
parameter-chart development. It is new evidence, not a claim that the old source
hash was recovered.

The file proves three statements: surjectivity permits a selection of actual
coordinate columns indexed by the output dimension; this injection extends to an
ambient coordinate permutation; the result applies to `ZMod p` for prime `p`.

The proof uses an independent spanning subfamily from Mathlib, constructs its
basis, compares its cardinality with the output dimension, reindexes it by
`Fin e`, and extends the resulting injection to a permutation. The selected
columns are evaluations of the original linear map on `Pi.single` coordinate
vectors. No minor is assumed and no positive-dimension hypothesis is added.

Attempt 01 failed on the name of a submodule equality lemma, a `letI` style lint,
and the explicit dimension argument required by `Fin.castAdd_injective`.
Attempt 02 fixes those three points and passes the portable Lean runner with
warnings treated as errors and default heartbeats. The two logs are retained.

The final module contains no admissions or custom axioms. The release gate is
responsible for independently compiling it and checking its axiom closures.
