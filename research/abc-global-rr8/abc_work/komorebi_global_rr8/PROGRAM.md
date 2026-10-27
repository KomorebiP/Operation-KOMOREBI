# Komorebi global arithmetic: RR8

Checkpoint ABC-20261025-RR8 continues the exact RR7 archive SHA-256
83c7020fd03361142fcac0567bd097c6b61c244f3a953c4618d13fd0cf4ead0a.
The user requested continuation of the independent arithmetic reconstruction
and ABC-height program within Komorebi. Earlier checkpoints remain pinned.

## Target contract

For each epsilon>0 find a triple-independent C_epsilon such that every
positive primitive integer a+b=c satisfies
log c <= (1+epsilon)log rad(abc)+C_epsilon.
The present checkpoint does not prove this estimate or improve its
unrestricted pointwise exponent. No IUT comparison is assumed.

## What the new construction supplies

1. Full translated norm tests recover exactly diagonal Z, and analogously
Z[i], from integral local coordinates and the real/complex coordinate.
Common-zero agreement need not be assumed. The Set-valued view category is
explicit. This is stronger global source recovery than the weak
three-coordinate norm balance excluded in RR7.

2. A fixed finite translation family, even together with finitely many
digit observations, can miss a high-precision local perturbation. Finite
resolution is recoverable at a supplied archimedean budget, with an
explicit finite observer construction. These statements have different
quantifiers and are compatible.

3. For every finite support S the genuine positive primitive additive
source is finite by the checked Evertse–Schlickewei–Schmidt theorem.
The entire {2,3} sector is classified by an elementary proof: up to
swapping a,b, its triples are (1,1,2), (1,2,3), (1,3,4), (1,8,9).

4. The checked classical Stewart–Yu theorem gives a stronger positive
global baseline:
log c < K R^(1/3)(log R)^3, R=rad(abc), with effective absolute K.
It supplies a conductor-dependent finite raw integer budget and an
explicit finite Komorebi defect diagram whose extension fiber is all
intended triples with R<=T. The numerical constant was not extracted.
The arithmetic estimate is imported, not claimed newly proved.

5. Supported precision alone is insufficient even for discrete integer
exponents: for every N>=4 there are unbounded pairwise-coprime
(4^u,9^v,25^w) of radical 30 satisfying a+b=c mod30^N while c>a+b.
Their ordinary defects are nonzero. They are not ABC counterexamples.
The exact unrestricted residue-preserving repair cost has logarithm at
the full height scale on this family.

## Actual dictionary

The raw integral adeles and mixed norm/reduction maps are Set-valued.
Translated tests use the same labelled integer in every completion and
ordinary local subtraction. Preservation by a multiplicative reduct is
not assumed. The effective finite diagram uses a finite set of ordinary
integer triples with an externally justified budget and a defect map to
Z/MZ. Its source completeness depends on the classical height theorem.

The prime-support observations remain nonlinear. No Hilbert-space
closed-range theorem is substituted for the arithmetic estimate. The
global comparison is with the intended integer source, rather than an
arbitrary coherent completion.

## Exact quantitative leaf

RADICAL_HEIGHT_ENVELOPE.md defines B(T), the largest c among genuine
primitive triples of radical at most T. Fixed-support finiteness proves
B(T) exists. Elementary triples give B(T)>T/4 for T>=4. The ABC target is
equivalent to log B(T)/log T tending to 1.

The imported effective estimate proves a much larger upper bound.
The next task is a genuine arithmetic reduction in its growth, not
another proof that the source can be reconstructed. The all-translation
tests hold identically on genuine points and yield no height inequality
on their own.

## Verification and limitations

Focused isolated reviews rederive the new proofs against exact file
hashes. Reviews are human-readable mathematical evidence, not formal
certificates. A positivity hypothesis error in a subsidiary modular
certificate was found and corrected; the original and correction are
preserved. No new Lean run or load-bearing mathematical computation was
performed. Earlier B04 Lean receipts were read as source reports only.

No historical novelty claim is made for the elementary or translated
classical statements. The full ABC goal and actual IUT witness
instantiation remain open.

