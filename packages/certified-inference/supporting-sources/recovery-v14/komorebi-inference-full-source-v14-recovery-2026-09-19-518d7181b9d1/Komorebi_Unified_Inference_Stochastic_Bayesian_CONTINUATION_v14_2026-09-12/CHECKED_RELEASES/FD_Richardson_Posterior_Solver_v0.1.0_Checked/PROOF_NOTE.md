# Richardson gain iteration to an actual posterior tolerance

## 1. Mathematical and computational contract

Use the unchanged v7 factor-coded rational model on arbitrary finite index types:

    P = L L^T,
    R = N N^T + sigma I,        sigma > 0,
    S = H P H^T + R,
    A = P H^T,
    v = y - H m.

Every rational is embedded exactly in the reals. The prior may be singular and
state/observation dimensions may differ. Complete rational self-adjoint packet
families are fixed throughout the iteration. The exact Gaussian-conditioning
and all-coupling quadratic-transport definitions are retained unchanged.

For an arbitrary rational initial gain B_0 and positive rational tolerance eps,
the executable Lean solver now provably returns a valid candidate with

    W2(actual posterior at y, Joseph Gaussian approximation at y) <= eps.

This is not only soundness of a successful return: the theorem proves that a
successful return exists within the explicitly computed finite update budget.
The ideal exact-arithmetic theorem is not a bounded-memory or floating-point
convergence guarantee. A physically capped Python run can honestly stop without
a certificate. Such a stop is not relabeled as mathematical failure or success.

## 2. Automatic rational step-size choice

Define

    Lambda = sigma + trace(S),
    tau = 1 / Lambda,
    rho = 1 - sigma/Lambda,
    q = rho^2.

The model's Gram witnesses imply S is positive definite and S >= sigma I. Its
nonnegative eigenvalues are at most trace(S), so the chosen Lambda is a valid
upper spectral cap. Lean derives Lambda>0 and 0<=rho<1, hence 0<=q<1, from model
validity; no eigenvalue estimate or innovation inverse is supplied as an oracle.

The additional sigma in Lambda makes the choice positive even for an empty
finite observation index type. The universal Lean development permits finite
empty types; the JSON producer follows its positive-dimension input protocol.
The bound is intentionally conservative, not an optimal Richardson step size.

RichardsonSpectrum proves Euclidean vector contraction under a generic certified
spectral interval. RichardsonEnergy applies it row by row to rectangular residual
matrices, using the Frobenius/Euclidean identities rather than an entrywise matrix
operator norm. RationalRichardsonGeometry transports the real inequality through
the exact rational embedding and derives the automatic model step-size bound.
A separate symbolic theorem handles a collapsed spectral interval: when the
lower and upper bounds coincide, the generic update makes the residual exactly
zero in one step. GeometricFuel covers q=0 without division by q or logarithms.

## 3. Exact residual recurrence and geometric certificate

Let F(B)=A-BS and update

    B_(n+1) = B_n + tau F(B_n).

RichardsonIteration proves the universal identities

    F(B_(n+1)) = F(B_n) (I-tau S),
    F(B_n) = F(B_0) (I-tau S)^n.

With E(F)=sum_ij F_ij^2, the proved spectral estimate yields

    E(F(B_(n+1))) <= q E(F(B_n)),
    E(F(B_n)) <= q^n E(F(B_0)).

For the exactCandidate producer, complete packet energy reconstruction gives

    sum_ab packet_energy_ab(F(B)) = E(F(B)).

Its exact score is consequently

    a(B) = E(F(B)) * (sigma + ||v||^2) / sigma^2.

All quantities in this expression are exact rationals. The new proof establishes

    a(B_(n+1)) <= q a(B_n),
    a(B_n) <= q^n a(B_0).

The old exact-certificate theorem therefore gives an actual-law estimate:

    W2^2(posterior, approximation(B_n)) <= ofReal(q^n a(B_0)).

Here the approximation is the Gaussian with mean m+B_n v and Joseph covariance

    (I-B_n H) P (I-B_n H)^T + B_n R B_n^T.

It is a valid law for every gain. Only the exact Kalman gain gives the original
model's exact conditional law by the retained conditioning theorem. The reference
posterior is the proved explicit version at the represented observation. No new
pointwise equality for independently selected canonical kernels is asserted.

## 4. A square-root-free, logarithm-free finite update budget

For eps>0 define the executable natural number

    N = ceil_N( a(B_0) / (eps^2 * (1-q)) ).

The rational inequality

    q^n * (1 + n*(1-q)) <= 1

is proved by induction. It gives q^n*a(B_0)<=eps^2 for every n>=N. Thus the last
permitted iterate passes the exact candidate checker and the tolerance checker.
The formula is a conservative termination witness; it is not presented as an
asymptotically sharp iteration estimate or a bit-complexity bound.

## 5. Executable search and total correctness

solveGainFuel checks both the full candidate checker and tolerance checker at
the current gain. If both pass it returns Some candidate. Otherwise it updates
the gain and decrements its finite fuel. With no fuel left it performs the final
check and returns None only when that check fails.

The proof is separated into:

- solveGainFuel_sound: every Some return passes both Boolean checks, with no
  a priori validity assumption needed for this conditional statement.
- solveGainFuel_complete: if the final permitted iterate passes, early stopping
  cannot return None.
- solveGain_terminates: model/packet validity and eps>0 imply a Some return at
  the automatically chosen N.
- solver_return_bounds_posterior: every Some return inherits the actual-law
  Wasserstein bound from v7.
- solver_reaches_posterior_tolerance: combines existence, both checks and the
  actual-law bound in one theorem.

The prior acceptance policy is also reused. The theorem
richardson_proposal_accepted shows that an exact Richardson next candidate is
accepted because it is valid and its exact score does not increase. This is
not monotonicity of the unknown true transport error, optimality, or a theorem
about a changing model or changing packet geometry.

## 6. Concrete kernel-reduced examples

GeneratedRichardsonScalar proves the actual solveGain return and iterate count
for P=H=R=1, m=0, y=1, B_0=0, eps=1/20:

    Lambda=3, tau=1/3, q=4/9, N=1440,
    early return after 4 updates,
    B_4=40/81, score=2/6561, W2<=1/20.

GeneratedRichardsonRotated has singular P=ones(2), H=R=I, m=0, y=(1,-1),
rotated rank-one packets, B_0=0 and eps=1/4:

    Lambda=5, tau=1/5, q=16/25, N=534,
    early return after 3 updates,
    B_3=(39/125)*ones(2), score=768/15625, W2<=1/4.

The return equations and gains are checked by decide +kernel. They are not
inferred from Python output. A finite DecidableEq instance for candidates
supports the executable Option equality check.

RichardsonBoundaryChecks additionally proves recognition of an initially exact
gain, rejection of a zero noise floor, no false success for a concrete zero-
tolerance run, an oversized-step energy-increase counterexample, and the generic
collapsed-spectrum one-step identity. Zero tolerance is not covered by the
positive-tolerance termination theorem.

## 7. Evidence and independent diagnostics

The active slice contains 64 modules: 50 unchanged inherited sources, 13 new
sources (including a decidable-equality support module), and one full axiom audit.
All have successful final-source compilation receipts. All 294 theorem/lemma
declarations, including 62 new declarations, are audited. Their axiom lists are
contained in propext, Classical.choice and Quot.sound. No placeholders, custom
axioms, unsafe proof shortcuts or native_decide occur in active sources.

The independent exact Python/SymPy diagnostics use 12 constructed dimension pairs
(state sizes 1..4, observation sizes 1..3), six recurrence steps per case, direct
principal-minor checks, matrix-power recurrence checks and exact stopping tests.
They passed 777 assertions and 11 invalid-input/export rejection checks. These
finite checks do not replace the universal Lean proofs and are not performance
benchmarks.

All 50 inherited active source modules were freshly checked in this run. The
pinned Mathlib cache was reused; unrelated historical continuous-time, moment-
bridge and other program modules were preserved, not all rebuilt. The seal
checks successful receipts and source/output/dependency hashes. It is not itself
a new Lean run. See FAILURE_LOG.md for unsuccessful drafts and time limits.

## 8. Boundaries preserved

- Exact factor-coded rational inputs, not uncertain real measurements.
- No floating-point rounding/enclosure guarantee and no parser/exporter proof.
- No automatic discovery of covariance factors for arbitrary matrix inputs.
- Positive tolerance; exact finite equality is not guaranteed for eps=0.
- Conservative iteration fuel, no polynomial bit-complexity or speedup claim.
- Fixed model and fixed complete packet geometry throughout the iteration.
- Certificate contraction does not imply stepwise true-error monotonicity.
- No full sequential filtering recursion, model-changing adaptation, generic
  transport metric axioms/optimal-coupling construction, or new Ito foundations.
- Richardson iteration is not presented as a new numerical method. No literature
  priority claim is made for the integrated formalization.
