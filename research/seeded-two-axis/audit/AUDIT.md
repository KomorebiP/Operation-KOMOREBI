# Mathematical self-review — v0.11.0

Primary verdict: **proved as written under the explicit source, rank, and cyclicity hypotheses** for K72–K82. This verdict is authoring-session self-review, not independent referee review or proof-kernel certification. Earlier retained proofs were not all re-audited.

## Target and routes

Continue the actual-profinite-source lifting problem left by v0.10.0. Three routes were executed: continuous obstruction/inflation, unrestricted free pro-p lifting, and a constructive abelian cyclic-centralizer test. The last gives a complete rank-two theorem. No general Galois or automorphic target is claimed closed.

## Dependency and obligation review

| Claim | Dependencies and critical checks | Result |
|---|---|---|
| K72 continuous next-step obstruction | Same exact square-zero matrix identity as K62; cochains and repairs continuous; finite discrete coefficients | Passed |
| K73 source inflation | Every continuous finite-valued cochain factors through one finite quotient; witnesses factor too | Passed; Milne II.4.2 checked |
| Carry counterexample | Correct sign for delta b, p odd, A^(p^2)=I mod p^3; negative sum certificate | Passed analytically and exact finite checks |
| K74 tower reconstruction | Residual adjoint action unchanged; inverse-limit continuity; finite branching requires topological finite generation | Passed; no claimed general finite horizon |
| K75 free pro-p lifting | Preimage of residual p-group is pro-p, including p=2; universal property through finite quotients | Passed |
| K76 procyclic powers | Binomial congruence includes p=2, s=1 and negative exponents; dense integers and completeness | Passed |
| K77 cyclic centralizer | Basis Q invertible over coefficient ring; equality on cyclic basis; nonscalar rank-two lemma includes F_2 | Passed |
| K78 cyclic normalized test | Normalization well typed modulo p^(n-a); integral cancellation only in torsion-free Z_p; finite polynomial outputs exact and continuous | Passed |
| K79 adapted horizon | Cancellation at finite level gives precisely modulus p^(n-a), not an inverse of p | Passed |
| K80 rank-two completeness | Minimal scalar depth makes selected normalized generator nonscalar mod p; all-scalar case separate; no extra constraints | Passed |
| K81 sharp horizon | Covers all primes; optimality only n,r >= 2; correction terms have depth at least 2n-1 | Passed |
| K82 mixed variance | Coefficient reduction, source inflation, and intertwiners checked directly; source descent requires kernel-triviality | Passed after correcting a preliminary draft description |

The rank-two positive theorem gives a concrete lift, not merely a vanishing invariant. Necessity addresses arbitrary higher-digit corrections, not just the selected constructive lift. A nonzero normalized commutator is therefore a valid negative certificate in the specified class.

## Counterexamples and retained distinctions

The pair I+p^(n-1)E12, I+p^(n-1)E21 has a continuous abelian realization modulo p^(2n-2) but none modulo p^(2n-1), preserving its level-n seed. On a free pro-p source arbitrary generator lifts do exist. Thus the obstruction belongs to an actual source relation.

The carry cocycle is nonzero on C_p but becomes a coboundary on C_(p^2). This refutes the inference that fixed-quotient nonliftability is automatically continuous-source nonliftability. It does not refute genuine source obstructions.

A preliminary draft treated both resolution coordinates as if they had unrestricted backward coarsening. The corrected K82 records opposite variance and explains why source inflation cannot be reversed for representations with nontrivial larger kernel action. No inherited theorem statement was changed by this correction.

## Computation evidence

All six suites passed. Bounds and exact counters are in the JSON reports, with commands, timeouts, elapsed times, environment, and before/after hashes in `checks/all_runs.json`. The new suite has no random sampling or floating tolerances. Higher-rank examples are constructed fixtures, not exhaustive coverage. The universal proofs are separate from the bounded checks.

An orthogonal enumeration computes the entire reduction image from admissible commuting pairs mod 8 and matches the classifier's positive set mod 4. This is an additional implementation check; it is not an independent mathematical review.

## Mechanical failures, corrections, and limits

- Lean and Lake were not found on PATH. No Lean build was attempted or claimed.
- A preliminary shell source-inspection command rejected a leading-hyphen printf argument. It was rerun without that argument; it had not changed source.
- Broad public-source searches returned unrelated pages. Those results were not used. Direct primary sources replaced them.
- CLI input validation was tightened to reject a top-level non-object JSON value. Five malformed-input cases now pass.
- No mathematical test failure occurred in this continuation. The mixed-variance correction was found in self-review before manuscript integration.
- The LaTeX build succeeded on the first integration build. Its final engine log has no warnings or overfull/underfull boxes. A terminal-environment message after latexmk was not a TeX engine error.

## Still unresolved

No completeness of this criterion for higher-rank noncyclic tuples, no general profinite finite horizon, no prescribed-determinant repair, no geometric Galois deformation condition, and no automorphic realization. Historical novelty and independent review remain unverified.
