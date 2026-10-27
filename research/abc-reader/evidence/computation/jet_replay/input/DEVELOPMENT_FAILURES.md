# Failures, corrections, and scope boundaries

## Mathematical correction

The previous conversational target Q=R^{o(1)}, where Q=abc/rad(abc), is false.
The primitive family 1+2^k=2^k+1 already refutes it. A stronger family proves that
any uniform bound Q^s <= C R^B polylog(c) must have B>=2s. The correct ABC defect
is Q/(ab)=c/R. See proofs/01_Target_Correction.md.

This retracts the corresponding global target, not the valid coefficient/local
valuation identities of the preceding jet filter.

## Failed candidate realization

Direct rational truncation of the Hankel determinant was attempted. After clearing
its denominators, every output prime p>K is a unit in the resulting scalar. It does
not retain the required output-c contact. The failure is proved and illustrated in
proofs/05_Truncation_Test.md; it is not inferred from a failed numerical search.

## Verifier implementation failure, corrected

When converting an exploratory unshifted moment determinant to the accepted shifted
moment determinant, the rank-one empty product used Python integer division and
produced a float. The exact identity test at rank=1, K=1, t=1/3 failed.
The run is preserved in verification/failed_shifted_run.log.
The formula was corrected to begin with Fraction(1, product(indices)).
The accepted verifier then passed in full. No float is used for a proof-bearing
number. Elapsed time is diagnostic only.

## Lean infrastructure failure

Lean and Lake were absent. Retrieval of a pinned official compiler/source failed
because the runtime could not resolve GitHub hosts. The .lean scripts are uncompiled.

## Not established

No global arithmetic scalar or adelic determinant-line section has been constructed
with both the local contact and the correctly normalized radical-scale height.
No product formula for the different polylogarithmic period values is assumed.
No ABC proof, no new global ABC bound, and no IUT Corollary 3.12 repair is claimed.
