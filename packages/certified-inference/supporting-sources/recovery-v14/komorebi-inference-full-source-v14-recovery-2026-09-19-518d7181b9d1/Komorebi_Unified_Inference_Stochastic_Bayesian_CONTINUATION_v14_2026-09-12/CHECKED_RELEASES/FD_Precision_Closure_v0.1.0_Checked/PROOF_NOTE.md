# Quantitative precision sufficiency and hybrid posterior certification

## 1. Scope and actual distributions

The reference input is the retained exact rational factor-coded Gaussian model:

    P = L Lᵀ,
    R = N Nᵀ + σ I,  σ > 0,
    S = H P Hᵀ + R,
    F(B) = P Hᵀ - B S,
    v = y - Hm.

State and observation spaces are arbitrary finite Euclidean coordinate spaces.
P may be singular, H may be rectangular, and the starting gain is arbitrary.
The packet families are exact complete self-adjoint rational projector families.

The retained probability development defines the actual explicit Bayesian
posterior η at y. For any represented rational gain B, the approximation is the
Gaussian with mean m+Bv and Joseph covariance

    (I-BH)P(I-BH)ᵀ + BRBᵀ.

The reference remains the same fixed model. Rounded evaluation of a certificate
is not uncertainty in model inputs. The guarantee uses the retained all-coupling
quadratic transport definition. The explicit-versus-canonical posterior boundary
is unchanged; no common exceptional-set claim is added.

## 2. What was missing and is now proved

The predecessor proved successful rounded returns sound, but did not establish
that enough precision forces a return. This release proves a computable upper
bound on the rounded score's inflation, selects sufficient precision, and
combines that result with the existing exact Richardson solver. The actual
hybrid program now has a successful-termination and posterior-tolerance theorem
for every strictly positive rational requested tolerance.

The gain iteration remains exact rational arithmetic. This is not a convergence
proof for rounded Richardson updates.

## 3. Local quantified radius bounds

Let h_p = 2^(-p), with p a natural number. The retained evaluator encloses each
exact rational x by a center-radius ball (c,r), meaning |x-c| ≤ r.
Its recentering operation is

    c' = floor(2^p c)/2^p,
    r' = ceil(2^p (r + |c-c'|))/2^p.

DyadicPrecision proves

    |x-down_p(x)| ≤ h_p,
    up_p(x) ≤ x+h_p,
    radius(round_p(b)) ≤ radius(b)+2h_p.

These estimates cover negative inputs. They use the same evaluator definitions
as the predecessor, not a substitute arithmetic model.

A computable Budget stores nonnegative numbers (M,k). Its soundness assertion is

    |x| ≤ M,
    the actual rounded ball encloses x,
    the actual radius is ≤ k h_p.

The budget constructors mirror the arithmetic graph exactly:

    input x:       (|x|, 2)
    addition/sub:  (M_a+M_b, k_a+k_b+2)
    product:       (M_a M_b, M_a k_b+M_b k_a+3k_a k_b+2)
    finite sum:    (sum M_i, sum k_i+2).

The product coefficient follows from h_p ≤ 1, center magnitude ≤ M+k, and the
full radius product term. No first-order error term is silently discarded.
Empty finite sums are covered by the universal theorem.

PrecisionMatrix and PrecisionModel propagate these budgets through the actual
rectangular matrix, model, residual, innovation, and packet evaluation graph.
The precision predictor uses magnitudes and radius coefficients. It does not
compute the exact residual, exact posterior, or innovation inverse.

## 4. Energy and full-score inflation

For a scalar budget (M,k), PrecisionEnergy proves

    x² ≤ energyUpper(ball)
       ≤ x² + 4k(M+k) h_p.

Sum these coefficients over every entry and packet. Let U,V be the exact
residual packet-energy sum and innovation energy, and U_p,V_p the rounded
upper bounds. The computed coefficients and magnitude bounds satisfy

    U_p ≤ U+a h_p,       U ≤ M_U,
    V_p ≤ V+b h_p,       V ≤ M_V.

With the exact positive noise floor σ, define

    C = [a(σ+M_V)+M_U b+a b]/σ².

The main arithmetic estimate is

    score_p(B) ≤ score_exact(B)+C h_p.

For valid complete packet geometry, the rounded score also bounds the exact
score from below. Hence the two-sided statement is

    score_exact(B) ≤ score_p(B) ≤ score_exact(B)+C 2^(-p).

No monotonicity of score_p in p is assumed or needed. The coefficient C is
conservative and may be large, particularly when cancellation makes the true
residual small. No optimal-precision or numerical-efficiency claim is made.

Key declarations:

    rounded_score_inflation
    rounded_score_sandwich

## 5. Computable sufficient precision

For a positive rational inflation allowance δ, define

    precisionFor(C,δ) = Nat.log 2 (Nat.ceil (C/δ)) + 1.

The zero coefficient is handled: the returned precision is 1. The integer-log
construction avoids a linearly oversized bit count. Lean proves, for every
p ≥ precisionFor(C,δ),

    C 2^(-p) ≤ δ.

Therefore, when score_exact(B)+δ ≤ ε², δ>0 and ε≥0, every precision above the
computed bound makes the original executable certifyRounded return its rounded
candidate. This is a theorem about the implemented evaluator and Boolean check.
It is not merely existence of some abstract sufficiently accurate arithmetic.

Strict exact-certificate slack score_exact(B)<ε² gives such a positive δ by
subtraction. The weaker assertion W2<ε is not enough: the chosen certificate
itself might be conservative. Equality at the certificate boundary is not
covered by the strict-slack completeness theorem.

Key declarations:

    coefficient_mesh_le
    rounded_score_le_with_slack
    certifyRounded_of_slack
    exists_precision_of_strict_score

## 6. Hybrid successful termination with no user-supplied slack

hybridSolve is an executable Lean definition:

1. Reject nonpositive ε.
2. Run the retained exact solver with target ε/2.
3. For its returned gain B, compute C and δ=ε²/4.
4. Compute p=precisionFor(C,δ).
5. Run the retained outward-rounded certificate evaluator at p.
6. Return the actual precision and candidate if its tolerance check passes.

The exact solver's successful candidate has score at most (ε/2)². A separate
minimality theorem proves that replacing conservative energy majorants by exact
energies cannot increase the score. Thus the exact gain's certificate has enough
slack for the rounded verifier. The computed p forces successful rounded return.

The top theorem states

    for every valid model and packet geometry, ε>0, and initial gain,
    there exist p,c such that
      hybridSolve(...) = some(p,c),
      checkCandidate(...) = true,
      checkTolerance(...) = true,
      W2(actualPosterior, approximation(c.gain)) ≤ ε.

Successful-return soundness is also proved without pre-assumed input validity.

Key declarations:

    exactCandidate_score_le_valid
    half_tolerance_slack
    hybridSolve_sound
    hybridSolve_terminates
    hybrid_return_bounds_posterior
    hybrid_reaches_posterior_tolerance

## 7. Early precision search with a guaranteed fallback

certifyTagged records the precision that actually succeeds. A finite schedule
succeeds if it contains any successful precision, with no sorting or monotonicity
hypothesis. A returned precision is proved to belong to the supplied schedule,
and its candidate is proved to be that precision's actual evaluator return.

hybridScheduled first obtains the same exact-solver gain, then tries any supplied
finite list of probe precisions followed by the computed sufficient precision.
It has the same successful-termination and actual-posterior guarantee as the
single-precision hybrid. Earlier success avoids evaluating the conservative
fallback. This is not resolution-changing adaptation; the model and packet
families remain fixed.

Key declarations:

    certifyTagged_origin
    certifyTagged_complete
    hybridScheduled_terminates
    scheduled_hybrid_reaches_posterior_tolerance

## 8. Concrete checked executions

The scalar example has P=H=R=1, m=0, y=1, initial gain zero, and ε=1/20.
The exact half-tolerance solver makes four updates and returns B=40/81, with
exact score 2/6561. The sufficient precision predictor returns 61 bits. Lean
kernel reduction checks this number, the solver return, the rounded score,
the actual hybrid return, and the posterior tolerance.

The singular two-state example has P=ones(2), H=R=I, m=0, y=(1,-1), rotated
rank-one packets, initial gain zero, and ε=1/4. The exact half-tolerance solver
makes four updates and returns B=(203/625)ones(2), exact score 3072/390625.
The predictor returns 72 bits; the actual hybrid return and posterior bound
are kernel-checked.

The scalar scheduled execution tries [4,12] before the 61-bit fallback. Four
bits produces score 1/8 and is rejected; twelve bits produces score 729/2097152
and passes. The actual scheduled program is kernel-checked to return at twelve
bits with W2≤1/20. The fallback need not be evaluated on this execution.

These are kernel reductions of executable Lean definitions, not claims inferred
from Python output. The coefficient and predicted precision are intentionally
conservative. The twelve-bit success does not invalidate the sufficient bound.

## 9. Verification and finite diagnostics

The active build combines 64 unchanged inherited modules with 18 new modules and
one all-declaration axiom audit. All 83 modules have matching successful
final-source receipts. All 386 theorem/lemma declarations, including 82 new ones,
were audited. Their axiom lists contain only propext, Classical.choice, Quot.sound.
Counts include support lemmas and regressions, not mathematical discoveries.

The source, attempted-source snapshot, log, compiled output, and direct dependency
hashes are checked before sealing. The 64 inherited active modules were freshly
rebuilt. Pinned Mathlib caches were reused; unrelated historical modules were
preserved rather than rebuilt.

Independent Fraction/SymPy diagnostics cover nine rectangular dimension pairs,
state and observation sizes 1..3, at six precisions per case. They check each
node's magnitude, enclosure, radius coefficient, energy inflation, and the full
score inequality. They also check invalid inputs, resource-limited returns, and
fallback behavior. The finite tests passed 9,651 assertions and 14 expected
input/export rejections. Three deliberately invalid Lean proofs were rejected.
Finite diagnostics are not the universal proof.

## 10. Remaining proof boundaries

- Gain iteration is exact rational; rounded gain-update forcing and convergence
  remain separate. No claim that fixed precision reaches all positive tolerances.
- The outward arithmetic uses dyadic fractional precision, unbounded integer
  parts, and exact terminal comparisons. It is not an IEEE-754/BLAS theorem.
- Inputs represent exact rationals, not uncertain measurements.
- Parser/exporter fidelity, rounded posterior-output arrays, and actual sampling
  implementations remain outside the theorem. The certified output is the
  mathematical Joseph Gaussian associated with the represented gain.
- The Python producer has explicit caps and may report RESOURCE_LIMIT. The ideal
  finite-termination theorem is not a hardware resource or bit-complexity bound.
- No monotonicity of unknown true error, optimal coupling, optimal bit count,
  model/packet-changing policy, sequential filtering, or new Ito theorem is added.
- Literature novelty and performance superiority are not established.
