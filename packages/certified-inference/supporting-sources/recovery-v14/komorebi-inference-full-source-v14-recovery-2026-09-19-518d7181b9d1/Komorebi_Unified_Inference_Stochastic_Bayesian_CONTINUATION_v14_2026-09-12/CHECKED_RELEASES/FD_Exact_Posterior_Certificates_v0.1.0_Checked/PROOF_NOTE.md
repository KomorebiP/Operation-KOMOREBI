# Exact numerical certificates for posterior error

## Scope

The input protocol consists of exact rational matrices H, L, N, complete rational
self-adjoint packet families Q and D, rational vectors m,y, and a rational scalar
sigma. It represents the real Gaussian model

    P = L L^T,             R = N N^T + sigma I,
    X ~ N(m,P),            Y = H X + independent N(0,R).

Every rational number is embedded exactly into the reals. A checker requires
sigma > 0. A Gram witness proves P positive semidefinite. A positive diagonal
floor plus a Gram witness proves R positive definite and its genuine Euclidean
quadratic lower bound. This is a factor-coded input protocol, not a theorem that
a factorization or a spectral floor is automatically found for any supplied
matrix. Rank-deficient priors and rectangular observation maps are allowed.

## Candidate and finite obligations

A candidate consists of a proposed rational gain B, rational local energy upper
bounds b_ab, and a rational innovation-energy upper bound V. Let

    S = H P H^T + R,
    F = P H^T - B S,
    v = y - H m.

The Boolean checkCandidate recomputes finite rational equalities and inequalities:

- sigma > 0;
- each packet family is symmetric, idempotent and pairwise annihilating;
- each family sums exactly to the identity;
- sum_ij ((Q_a F D_b)_ij)^2 <= b_ab for every packet pair;
- sum_j v_j^2 <= V.

No claim made by a producer is accepted in place of these computations. In
particular, an underestimated or negative local bound can be rejected even when
its claimed global score looks attractive. Nonnegativity of the total upper bound
and of V is derived from the successful checks.

The exactCandidate function is itself an executable Lean definition. It computes
the local energies and innovation energy exactly. Its generic validity theorem
needs only the positive floor and packet-geometry hypotheses.

## Real semantics and posterior guarantee

RationalMatrixCertificates proves the rational-to-real map preserves zero,
identity, addition, subtraction, scalar multiplication, transpose, finite sums,
matrix multiplication and matrix-vector multiplication. RationalPacketCertificates
constructs the real SelfAdjointPackets object from the rational checks and proves
complete coverage. RationalModelSemantics identifies the real gain residual,
innovation vector, covariance validity and noise floor.

Define the rational squared-error score

    score = (sum_ab b_ab) * (sigma + V) / sigma^2.

For any candidate whose exact checker returns true, the main theorem proves

    wasserstein2Sq(actualPosterior, JosephApproximation(B)) <= ofReal(score).

The actual posterior is the explicit posterior version established by the retained
Gaussian-conditioning theorem. The approximation is the Gaussian law with mean
m+B(y-Hm) and covariance

    (I-BH)P(I-BH)^T + B R B^T.

It is a valid probability law for arbitrary B. The result is not a claim that an
arbitrary gain is the original model's exact Bayesian gain.

The all-coupling Wasserstein infimum, its nonnegative extended cost, and the
explicit-posterior semantics are retained unchanged from v5/v6. No new assertion
about optimal couplings or the general metric axioms is made.

For rational epsilon >= 0, the square-root-free check

    (sum_ab b_ab)*(sigma+V) <= epsilon^2*sigma^2

implies wasserstein2(actualPosterior, approximation) <= ofReal(epsilon).
No exact innovation inverse, exact Kalman gain, exact posterior covariance or
floating-point eigenvalue computation is required by this certificate.

## Acceptance and finite batches

acceptCandidate replaces an incumbent only when the proposed certificate passes
checkCandidate and its rational score is no greater than the incumbent score.
Otherwise it returns the incumbent unchanged.

The checked acceptance theorems prove preservation of certificate validity and
non-increase of the selected score. List.foldl gives the same guarantees for any
finite list of untrusted proposals. The probability bridge proves that the selected
approximation is bounded by the incumbent's certificate; an already-certified
posterior tolerance survives the batch.

This is non-increase of an upper certificate. It does not imply strict improvement,
non-increase of the unknown true error at each accepted step, progress of an
arbitrary proposal generator, convergence to a zero residual, or global optimality.
The model and packet resolutions are fixed throughout a batch.

## Executable examples and trust boundary

checks/exact_certificate.py implements exact Fraction arithmetic, validates shapes,
and rejects JSON floating-point numbers. JSON integers, p/q strings, and decimal
strings represent exact rational numbers. A decimal string is not an enclosure of
an unknown measurement. The producer supports positive dimensions up to its explicit
input caps; the universal Lean theorems are stated for arbitrary finite index types.

Python output alone is NOT a Lean certificate. The exporter writes the full exact
model, packets and candidates into a Lean module. The module proves the checker
outcome by decide +kernel (kernel reduction) and applies the generic posterior theorem. It does not
use native_decide, custom axioms or placeholders. Parsing and export fidelity are
not separately formalized: the certified mathematical input is the explicit input
in the generated Lean source, which must correspond to the user's intended data.

The scalar example selects B=49/100 with score 1/1250 and certifies W2 <= 1/20.
The two-state example has singular P=ones(2), H=I, R=I, y=(1,-1), and rotated
rank-one packets. It selects B=(5/16)ones(2). Conservative local bounds give
score 15/256 < (1/4)^2. An invalid negative-bound proposal is rejected; a valid
proposal with score 300 is rejected after selection of the smaller certificate.

The independent Python tests cover twelve constructed rational dimension pairs,
state sizes 1..4 and observation sizes 1..3. SymPy supplies a second exact matrix
implementation and trace-Gram energy checks. Negative tests exercise insufficient
bounds, incomplete packets, a nonpositive floor, malformed inputs and floats.
These finite diagnostics do not establish universal soundness; the Lean proof does.

## Remaining boundaries

- General interval input uncertainty and verified floating-point enclosures.
- Automatic witness/floor discovery for arbitrary covariance input formats.
- Proof of parser, serializer, or an external numeric producer's implementation.
- A solver-specific contraction and iteration-to-tolerance theorem.
- Model-changing or packet-changing adaptive policies.
- Full finite-horizon filtering kernel recursion and continuous-time stochastic foundations.
- Literature novelty or numerical performance superiority.

The older canonical-kernel almost-everywhere scope remains unchanged. All new
certificate applications use the explicit posterior version at the represented
observation. No new cross-model canonical exceptional-set assertion is made.
