# Versioned claim ledger: ABC-20261025-RR4

Parent is the archived RR3 checkpoint pinned in LATEST.md. The target remains
every-epsilon primitive integer ABC. It has not been reached. Prior checkpoints
are preserved, and their claims are not upgraded by the present computations.

| ID | Exact result | Proof and review |
| --- | --- | --- |
| PT1 | Nested phases have exact congruence compatibility and child counts; a captured first-contact floor persists under refinement | [Refinement proof](routes/refinement/PROOF_NOTE.md), [review](reviews/refinement_multichannel.md) |
| PT2 | Zero-phase blocking conserves W G, can move lifting into birth, and obeys exact cyclotomic product divisibility and D_n<=M D'_t | Same proof and review |
| PT3 | A smaller-exponent compression preserves W and has U(s_n)/U(s_m) dividing n; D_n<=m shows its criterion is already covered by RR3 | Same proof and review |
| PT4 | All unrestricted integer finite-tap outputs at stride h form gcd(s_n,A^h-B^h) Z; two Bezout taps attain the positive generator | [Tap proof](routes/taps/PROOF_NOTE.md), [review](reviews/taps.md) |
| PT5 | Primitive stride 2n has positive minimum s_n; half-order sum taps lose odd birth contact; vanishing moments amplify depth and height together | Same proof and review |
| PT6 | Preserving selected birth powers P requires P dividing T(A)-T(B); a nonzero difference has the proved norm/degree bound and exact attainable minimum P(A-B) | Same proof and review. Optimal fixed-support norm/degree tradeoffs remain open |
| PT7 | Integral analysis/synthesis preserves minimum coordinate valuation; individual functional depth may move into synthesis cancellation | [Multichannel proof](routes/multichannel/PROOF.md), [review](reviews/refinement_multichannel.md) |
| PT8 | Simultaneous channel depth has a determinant cost; adaptive normalization must track inverse coefficients; strict square integer Laurent paraunitarity forces signed monomial permutations | Same proof and review |

Written proofs are elementary apart from the already proved upstream lifting
identities, whose source is retained. The cited signal-processing material
supplies the operation dictionary rather than an unverified arithmetic
inequality. No historical novelty, external peer review, or formal Lean
certificate is asserted. Separate agent agreement is not a proof certificate.

The tests are finite assertions in exact integer, modular, and rational
arithmetic. Their version 2 manifests are in `computation_records/` and have
run status completed with validated input/output hashes. Universal statements
rest on the proofs and reviews, not their finite case counts.

Two scope clarifications were applied during review: the pointwise target
exponent is positive even though the ambient sequence includes index zero;
the coprime-radix all-phase claim applies to baseline depths k<=e_p. The
higher-depth statement retains its full modulus and its dependence on p.
No load-bearing identity was changed by those restrictions.

The attempted bridges that did not provide the missing estimate are: fewer
compatible phase paths at an already known contact, degree reduction without
base-height normalization, moment divisibility without degree-height cost,
and perfect reconstruction without retaining the selected functional.
These failures do not prove that all adaptive polyphase/tap methods fail.

The full ABC target, a new uniform high-order radical estimate, and the
existence of a sufficiently small nonzero preserving adaptive certificate
remain open. The RR3 sufficient cutoff is unchanged.
