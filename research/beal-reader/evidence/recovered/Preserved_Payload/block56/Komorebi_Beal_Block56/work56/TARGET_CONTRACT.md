# Block 56 target and dependency contract

Sole authoritative predecessor: Komorebi_Beal_Block55_Maximal_Order_Kummer_v5.5.0.zip

SHA256: 4fcbe7e557140656fd4bae27793043df19fdc680e95ad4d6277a76fbb7182cea

The original bytes are preserved in predecessor/. No predecessor is edited.
The startup verifier passed, including its selected nested replays, before
new source or theorem files were written.

## Goal and bounded target

The long-term goal is elimination of the retained reducible branch of
A^3+B^5=C^7. The immediate target is a same-representation obstruction to
an explicitly stated realization of the surviving 97/293 first layer.

Success here means a proved necessary Frobenius condition, an exact reduction
of a specified actual branch to finite good-reduction data, and verified
exclusion of that branch. It does not mean eliminating the entire reducible
branch, the complete signature, or Beal.

The achieved exclusion is depth n>=2 under the COMPLETE high-support
hypothesis H(C) subset {97,293}. It is not an exclusion of the same highest
character-layer support when other high primes may also divide C.

## Inherited inputs retained as hypotheses

G1. K=Q(sqrt5), E=Q_7(sqrt5), O=Z_7[phi], phi=(1+sqrt5)/2. The hypothetical
primitive positive solution lies in the exact retained reducible branch.
The Jacobian is that of Z^2=X^6+10BX^3+12AX+5B^2, and the even quadratic
twist is the one inherited from Q(zeta15)^+/K. Its rank-two representation
has determinant chi_7. At good auxiliary primes its underlying four-dimensional
Frobenius is restriction of scalars of the rank-two E representation.
The twist is unramified there. The defining radicand is 3(5-sqrt5)/2.

G2. One actual natural basis has lower-left entries in 7^n O for the finite
actual depth n>=1. Modulo 7^n, its diagonals are chi_7*eta_n and eta_n^(-1).
This is not a modulus selected by a new point-count test.

G3. The actual global character obeys eta_n=1 modulo 7^(floor(n/2)+1),
as in Block 53. In particular this applies to the same Frobenius matrices.
This is an inherited written geometric/character theorem, not certified
by the new finite-field runs.

G4. The retained support arguments supply a nonzero opposite class beta with
some variable ramification. At its support n=t+2s, t=1+v_7(v_q(C)), and
trivial eta implies s=0 and h>=n. These inputs are used only for the optional
remaining depth-two multiplicity statement, not for the new Frobenius exclusions.

G5. The five-row ray presentation and Kummer coordinates from Block 55 are
used to preserve the old abstract survivor and interpret the local controls.
They are not needed to prove the good-197 or good-491 obstructions.

The complete original input files and 13 named source leaves are pinned in
source_records/INHERITED_INPUT_HASHES.json, including the nested Block 52
Frey model and Frobenius convention. Hashes establish provenance, not truth.

## Executed routes

A. Same-representation good Frobenius: derive precision r=min(n,m+h), then
count the exact Frey reductions at 197 and 491. Successful stated exclusions.

B. Direct ramified-local contradiction for 97/293: test the full toric
relations together with trivial local Frobenius correction. Two exact local
models survive, so these local constraints alone do not give a contradiction.

C. Generic Weil-polynomial exclusion: test whether the strengthened precision
and Weil condition suffice without using the actual Frey locus. Explicit
compatible Weil polynomials survive. The actual curve counts are essential.

## Evidence standard

The new mathematical arguments are written and self-reviewed. The finite
assertions have two implementations with distinct field models and orbit
normalizations. Independent code is not independent mathematical review.
No new Lean compilation, new Lean certificate, or global novelty claim is made.
Timeouts are inconclusive. No global completion percentage is assigned.
