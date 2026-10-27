# Cached selective inference — checked construction

Author: Komorebi P. Base checkpoint: v13,
SHA256 8f6bde58df0b6b18388f60adff4a22e5fed0a69d0a8f66321922452950cf3ba7.

## State, initialization, and precomputation

Retain the exact model P=LL^T, R=NN^T+sigma I with sigma>0, innovation
S=HPH^T+R, and residual F(B)=PH^T-BS. The output projectors Q_a are complete,
self-adjoint, and mutually orthogonal. Input projectors retain the same assumptions
for the final inherited certificate. Write E(X)=sum_ij X_ij^2.

Precompute K=(tau,T,w), where

    tau = 1/(sigma+trace S),  T = I-tau S,
    w = (sigma+||y-Hm||^2)/sigma^2.

A cache state is (B,G,e,total), with the invariant

    G_a = Q_a F(B),  e_a = E(G_a),  total = sum_a e_a.

Initialization computes F(B) once, forms all projected residuals and their energies,
and sums the energies. `initialState_valid` proves its validity directly. Complete
output accounting then gives total=E(F(B)) and score(K,c)=total*w=a(B).

## The actual cached update

Choose a by running the finite maximum scan on the stored energies. Compute

    B' = B+tau G_a,  G'_a = G_a T,  e'_a = E(G'_a),
    G'_b = G_b and e'_b=e_b for b != a,
    total' = total-e_a+e'_a.

The definition updates only the selected residual/energy. It does not recompute
F(B') or all projected residuals. `step_valid` proves every invariant for the new
state using the v13 selected/unselected residual identities and a finite-sum update.
`step_other_residual` and `step_other_energy` expose unchanged entries.

The Kernel parameter must be `prepare M` for the semantic invariant theorems.
Arbitrary supplied model constants are not assumed correct. The canonical solver
computes this Kernel internally. Likewise its cache starts from initialization,
not an unvalidated externally supplied state.

## Equivalence and finite success

`chosen_eq` proves that scanning valid cached energies chooses exactly the label
obtained from recomputed energies. `advance_gain` identifies its gain step with
the v13 greedy step. Induction gives, for every natural n,

    cachedTrajectory(n).gain = greedyGain(B0,n).

The same induction proves validity of every cache state. Thus the v13 geometric
rate r=1-(1-q)/A, q=(1-sigma/(sigma+trace S))^2, applies, where A>0 is the number
of output labels. The seed inhabits that label type and supplies nonemptiness.

    score(cache_n) = a(B_n) <= r^n a(B0).

The inherited computable fuel

    N = ceil_nat(a(B0)/((epsilon/2)^2*(1-r)))

therefore guarantees score(cache_N)<=epsilon^2/4.

`search` tests the exact cached score at every step. If it exceeds epsilon^2/4,
it advances and decrements fuel. Otherwise it returns the state. At fuel zero,
it still tests the last permitted state. `search_complete` proves success from
the sufficient last-state score. `search_origin` gives an actual index k<=N,
and `search_score` proves the passing cached-score bound of any returned state.

## Final verification and parameter output

`solveCached` checks positive epsilon, valid setup and complete scan coverage,
precomputes the model Kernel, runs the cached search, then calls the inherited
`certifyGain` only on the returned gain. It tries the requested precision probes
and a sufficient fallback with inflation allowance epsilon^2/4. The search's score
bound supplies the strict slack required for this fallback to pass.

`solveCached_sound` uses the final independent verifier and needs no caller-supplied
validity assumptions. `solveCached_terminates` proves successful return under the
valid-input hypotheses. `cached_solver_gain_origin` proves the returned gain is an
actual v13 greedy iterate at an index within fuel. The posterior theorem applies
the inherited exact Bayesian semantics and Wasserstein certificate.

`runCached` then invokes v12's output representation at positive delta. It returns
the existing Result record and proves the existing ResultValid proposition:

    candidate/tolerance checks pass,
    W2(actual posterior, Joseph Gaussian at returned gain) <= epsilon,
    mean/covariance output intervals enclose that same Gaussian's parameters,
    every radius <= delta,
    reported parameter precision and arrays equal the actual evaluator.

The canonical theorem is Komorebi.CachedPosterior.runCached_terminates. Output
arithmetic, Gaussian semantics, and parameter interpretation are unchanged.

## Executions

The coordinate example now uses six selective updates because search deliberately
waits for the stricter epsilon^2/4 exact-score margin. The rotated example uses four.
These differ from v13's early rounded-verifier stopping after five and three. The
benchmark recomputed-selective baseline uses the SAME stricter stopping condition,
so its gain sequence and returned candidate match cached execution exactly.

GeneratedCachedCoordinate and GeneratedCachedRotated check the computed fuel,
actual gain, exact and rounded scores, every selected label, solver return, output
precision, all reported centers/radii, and ResultValid. The 21 benchmark modules
instead check explicit final candidates and posterior tolerances. They do not
claim their Python timing traces are Lean-verified execution traces.

## Rounded-cache boundary

For the scalar model P=H=R=1, y=1, m=0 and B0=0, tau=1/3. The first exact step
has B1=1/3 and F1=1/3. Independently rounding both to zero fractional bits yields
stored gain 0 and stored residual 0. The stored score is zero but the true residual
score at gain zero is two. `naive_cache_invalid` formally rejects this state.
`naive_final_verification_rejected` proves the independent final verifier rejects
it at epsilon=1/10. Soundness survives the verifier; the naive rounded cache cannot
supply the exact-invariant termination proof.

This refutes that naive implementation route, not the possibility of a correctly
enclosed rounded cache. Such a cache requires a separate perturbation/error budget.
No rounded-selective convergence theorem is claimed in this release.

## Computational interpretation

The Python reference stores packet matrices and energies explicitly. It reuses
unchanged objects and updates total by a scalar difference. Tests inspect these
invariants against independent scalar model/residual formulas. The matrix backend
skips zero left multiplicands in every compared method. Work counters describe its
iterative scalar matrix operations and comparisons; they omit preprocessing and
certificate arithmetic and are not a formal bit-complexity theorem.

The final evaluator still computes a full certificate. Moving it outside the loop
removes repeated attempts but does not make the final check local. Full residual
reconstruction is also performed by the independent exported candidate checker.
Consequently the release demonstrates cheaper selective iteration, not a universal
full-cost advantage. See BENCHMARK_REPORT.md for the measured limit.
