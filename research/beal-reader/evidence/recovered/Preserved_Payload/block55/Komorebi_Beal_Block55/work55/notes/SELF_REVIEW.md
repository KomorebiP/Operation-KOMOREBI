# Adversarial self-review

The reviewer is the same assistant as the author. This is not independent
mathematical review or Lean verification.

1. GLOBAL EXPONENT, NOT A LOCAL GUESS. e is the exponent of the entire actual
eta image. Therefore Frobenius at every place has the precision L=n-e. An
inertia exponent alone would not imply that precision. The explicit n5,
Q491 counterexample demonstrates the distinction.

2. SAME BASIS. The bound on F22 and the factorization yr=F22-1 refer to one
natural basis. There is no independent local re-diagonalization.

3. BETA NOT REQUIRED. The maximal-layer proof uses j=t+s, not exact beta
ramification t+2s=n. It deliberately covers N21 of valuation larger than n.
The finite checks include6080 such instances.

4. TOP LAYER ONLY. Lower-order inertia can have nonzero alpha. No claim says
all eta support is contained in alpha's local zeros. The criterion uses only
eta^(7^(e-1)), which remains a nonzero global character.

5. UNRAMIFIED AMBIGUITY. A nonzero highest layer must have nonzero inertia,
using class number one or the inherited residue-generated ray presentation.
This would fail without the class-group input.

6. MATCHED LOG COORDINATES. Kummer rows and reciprocity columns use one
surjective residue logarithm at each place. A column rescaling changes both
and changes the dual character coordinate inversely. The independent field
implementation respects that equivalence.

7. NO FAKE DESCENT. Forty-two F7 tests work because every F49 zero set is
contained in an admissible F7 zero set. The actual alpha remains arbitrary
in F49. A separate rank2 condition really does force descent, but only when
it occurs in actual maximal support.

8. CIRCUIT BOUND IS NOT SUPPORT SIZE. A small minimally dependent subset lies
inside actual maximal support. Its coefficients need not be the actual
character coordinates, and the actual support may be much larger.

9. CONSERVATIVE HIGH SUPPORT. Both places of each split rational divisor are
allowed, without assuming paired actual ramification. Arbitrary primes with
h<=1 cannot ramify in eta and are allowed in every arithmetic application.
Adding a high-h prime can invalidate the criterion; no such addition is hidden.

10. DEPTH BOUND AFTER ETA VANISHES. Trivial eta only forces s=0,n=t,h>=n at
beta support. It does not force beta=0. The h2 and h3 multiplicity cases are
retained. A ratio condition at1373 does not kill the bad13 unit coefficient.

11. NONEMPTY NECESSARY SYSTEM. The97/293 line survives all new first-layer
tests. A universal vanishing claim from this block's criterion alone would
be false. Its global ray character need not be a Frey diagonal.

12. PROVENANCE AND COVERAGE. Original archive bytes and named inputs are
pinned. Fresh outputs are required by the release verifier. Exact finite
checks and independent implementations do not certify the upstream geometric
leaves, the classical source theorems, or global novelty.

Assessment: the supplied written reductions are coherent under their stated
hypotheses. Residual risks are the unformalized arguments and inherited
geometry. The finite certificate has been reproduced by a separate
implementation with different field and rank procedures.
