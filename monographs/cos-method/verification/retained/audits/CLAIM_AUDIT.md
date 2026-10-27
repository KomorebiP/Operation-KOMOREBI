# Independent claim audit: Quadratic-Form Engine / K-COS

Audit date: 2026-10-07. This is a fresh derivation from the raw current TeX and implementation, performed in a separate agent session before consulting earlier audit verdicts. Agreement between agents is not a mathematical proof. This report concerns the original supplied revisions; staged corrections require a separate review.

**Normalized claim.** A finite Gaussian quadratic form reduces to a weighted chi-square law; exact factor streaming preserves that operator; bounded phase pruning and range residuals enclose its spectrum; query-dependent centered packets bound transform approximation; and a directed-arithmetic exact-spectrum backend encloses the positive central tail. A dense binary64-factor postcheck can propagate a verified spectrum into a tail bracket.

**Primary verdict: incomplete, with the smallest missing implication.** The mathematical reduction, packet/error bounds and matrix postcheck reconstruct correctly under the restrictions below. The original implementation does not prove that its advertised accuracy acceptance and serialized matrix-tail endpoints retain outward enclosure: some endpoint strings pass through ordinary precision, and the acceptance ratio is evaluated as a point approximation. This is a repairable implementation gap, not a counterexample to the underlying spectral or tail inequalities.

## Audited revisions

| Raw artifact | SHA-256 |
|---|---|
| `FINAL_MANUSCRIPT.tex` (v1.9) | `c67d50ceaff074af9bbf345ac572f71bfc585a77c6afbc53265ffed088a9a03c` |
| `K-COS_Query_Adaptive_Spectral_Packetization_v0.1.tex` | `438eccf26739f3ab0300fa9b8075bcd681f841d2b77b9c843026b6433f2953d1` |
| `accuracy_driven.py` | `cfff92b9c839f9e798d882bf5a6edf6a9bdebfd4dc91d8edde4c386314ea7c5f` |
| `verified_spectrum.py` | `7a8b03c6ae0ea6abffbbb1a462968c3634844c4621ca0637f7c6952913f4d731` |

No applicable `AGENTS.md` or `.mathbox` ledger was found in the supplied project. The proof-audit skill's general logic, computation-dependent and external-source obligations were applied. Historical novelty and external bibliographic claims were not audited here.

## Dependency graph

1. Covariance square root + orthogonal diagonalization + Gaussian rotation invariance → central signed reduction. PSD quadratic matrix additionally eliminates stochastic linear terms in null directions → noncentral positive reduction.
2. Factor column partition + finite matrix multiplication → streamed `A`, `A^T`, `AA^T`, `A^T A` actions → exact partition invariance and exact-arithmetic Krylov equivalence.
3. Orthogonal phase decomposition + triangle inequality → block-norm envelope → noncommutative telescoping → pruning and edge-additive bounds.
4. Orthogonal range basis → PSD core/residual split → residual moments and determinant identity → Chernoff upper bound; compact orthogonal residual completion → exact recovered nonzero spectrum.
5. Positive spectrum + admissible tilt → centered-log series and its remainder → finite-grid exponential perturbation bound → packet contribution to tail error.
6. Positive support + cosine folding + Chernoff bound → support/alias error; characteristic-function modulus + frequency decay → omitted-mode error.
7. Directed finite arithmetic + conservative analytic error bounds → a logarithmic tail enclosure. Directed serialization and directed acceptance arithmetic are additional required leaves.
8. Exact dyadic factor + interval candidate postcheck → coefficient enclosures; coefficientwise Gaussian coupling + endpoint tail enclosures → matrix-defined tail interval.

The mathematical dependencies are acyclic. “Eigensolver returned a candidate” is not a correctness dependency: the reconstruction/orthogonality postcheck supplies it.

## Obligation matrix

| Claim/obligation | Result | Exact scope or correction |
|---|---|---|
| Central positive/signed reduction (v1.9 core) | Passed | Finite real symmetric matrices and PSD covariance. Zero eigenvalues can be omitted; rank zero is a deterministic boundary case. Signed MGF endpoint maxima/minima over empty sets require the usual infinite-endpoint convention. |
| Noncentral positive reduction | Passed | `q0` is the squared norm of the component of `M^(1/2) mu` perpendicular to `range(M^(1/2) S)`. This is the precise geometry behind “deterministic contribution.” |
| Streaming and partition identities | Passed | Exact arithmetic, replayable block access, same data/weights/covariate basis. Floating accumulation order gives numerical agreement, not bitwise equality or directed certification. |
| Phase transfer, pruning, polynomial and additive edge risk | Passed | Finite orthogonal projectors resolving the identity; retention consists of complete phase blocks; the norms appearing in formulas are exact quantities or proved upper bounds. Floating norm estimates alone are not machine certificates. |
| Equal-cost sorted-risk optimality | Passed | Optimal cardinality only for the stated scalar additive certificate. No global optimum claim follows for exact-envelope refinement, unequal costs or two simultaneous budgets. |
| Frontier-to-I/O reduction | Correct with explicit access assumptions | Exact graph is already known/validated; blocks lie wholly inside structural phases; required factor action and fixed metadata remain available. Graph construction may require all input. Mixed-phase blocks cannot automatically be skipped. This is not an I/O optimality theorem. |
| QR-core spectral equivalence | Restriction needed | State that `Q_perp` has orthonormal columns and `Q^T Q_perp=0`. `F=Q_perp R_perp` alone proves the displayed factor identity but not equality of singular spectra with the core. |
| Tiled memory law | Restriction/correction needed | Resident covariate rows cost `tp`: use `O(tc+pc+tp+t^2)` or assume `p<=c`. Output storage, source storage and library workspace are excluded. |
| Block-norm operator domination / Weyl coefficient interval | Passed | For symmetric error, `||E||2<=||C||2`; min-max with `-eps I <= E <= eps I` supplies the eigenvalue comparison. |
| Trace–Frobenius–cap MGF envelope / residual rank | Passed | PSD core and residual, admissible positive tilt, exact or correctly directed moment bounds. Zero residual is handled separately before division. Integer rank claims must use outward bounds in the correct directions. |
| Centered packet expansion (v0.1) | Passed in CGF domain | Explicitly state `Re s<1/(2 lambda_max)` and use the analytic log branch normalized at zero. Packet radius `<1`, order a nonnegative integer, finite nonempty packets. |
| Finite-grid packet-to-tail and combined analytic bound | Passed | Exact mathematical arithmetic; nonempty positive spectrum, admissible positive tilt, `q>=0`, `b>q`, mode count `N>=1`. This is an analytic approximation bound without floating rounding control. |
| Support folding and omitted-mode bounds | Passed with justification below | Use folded measure/Fejér convergence to avoid an unexplained pointwise cosine-series assumption. The beta-mode bound applies at every positive rank; the implemented interval power bound separately requires rank `>2`. |
| Finite analytic refinement | Passed | Fixed finite positive spectrum and upper-tail query `q>sum lambda`; singleton packets remove representation error. This proves finite existence, not every greedy schedule's termination or optimality. |
| Exact-spectrum interval enclosure theorem | Correct after stated restriction | `q>=0`, `U>q`, `K>=1`, positive rank `>2`, `0<theta<eta<1/(2 lambda_max)`. Current parameter designer enforces stronger `q>sum lambda`. All checks/error bounds must be directed or exact. |
| Original advertised accuracy acceptance | Failed as a universal machine guarantee | `accuracy_driven.py` evaluates point `mp.expm1` and parses tolerance at ambient precision. “High precision” does not prove an upper bound at an arbitrarily tight acceptance boundary. |
| Candidate eigensystem postcheck theorem | Passed | Sorted nonnegative `d_i`, square candidate `Q`, `eta<1`, directed upper bounds for orthogonality/reconstruction norms. PSD `H` allows clipping lower endpoints to zero. |
| Original matrix-tail serialization | Failed | `_parse_log_interval` rounds endpoint strings at ambient point precision; width is formed before `workdps`, and returned endpoints are reformatted from rounded values. Literal outer strings must be preserved. |
| Numerical experiments | Not re-certified here | Stored agreement and overlap support finite validation. They do not independently prove enclosure, every threshold, universal speedup or priority. |
| Lean status | Out of scope for this raw-source audit | No theorem here becomes a Lean proof because a ledger claims it; final supplied Lean sources and build output need separate checks. |

## Decisive evidence and exact fixes

### Acceptance and matrix endpoint precision

In original `verified_spectrum.py`, `_parse_log_interval` creates `mp.mpf` values outside an explicit high-precision or interval context. For the legal literal interval

`[-1.00000000000000000001, -0.99999999999999999999]`

both endpoints round to `-1` at the default 53-bit point precision. The width then becomes zero; later increasing working precision cannot recover discarded bits. The resulting serialized singleton loses the outer enclosure. This counterexample targets the helper and its use, not the analytic enclosure theorem.

Keep original literal lower/upper strings. Evaluate their difference and `expm1(log(10)*width)` in directed interval arithmetic. Accept only if the resulting ratio's upper endpoint is no larger than the requested tolerance's lower endpoint. Do not parse the tolerance as an ambient-precision point first. Keep display summaries separate from authoritative endpoints. The numerical-validation agent was notified and is correcting the staged source.

### Negative thresholds in the enclosure derivation

The integral `I_k=integral_q^U exp(-theta(x-q)) cos(k*pi*x/U) dx` is an integral of the density folded onto `[0,U]`; it requires `q>=0`. With `Q=chi-square_3`, `theta=0.1`, and `q=-1`, its infinite-window/infinite-mode limit contains the true tail `1` plus the strictly positive term

`integral_0^1 exp(0.2*y) f_chi-square_3(y) dy`.

Meanwhile the stated support and series remainders can tend to zero. Thus extending this derivation to negative `q` would be false. Return exact probability one for `q<=0` or restrict the backend theorem; the current controller already rejects queries at or below the mean.

### QR factorization hypotheses

Take `A=e1`, `Q=e1`, `R=1`, `U=e2`, `Q_perp=2*e2`, `R_perp=1/2`. The displayed update factor identity is true, but the updated Gram eigenvalues are `(1,1)` and the unweighted core Gram eigenvalues are `(1,1/4)`. Requiring an orthonormal complement fixes the statement.

### Cosine representation leaf

Fold the tilted positive measure into `[0,b]`; its cosine coefficients are `Re phi_theta(k*pi/b)`. The folded law has an integrable density and no atom at the payoff discontinuity. Fejér sums converge under integration against the bounded piecewise continuous payoff. The integrated ordinary series is absolutely convergent because `|J_k phi_theta(u_k)|=O(k^(-1-r/2))` for every positive rank. Its Fejér and ordinary sums therefore agree. This establishes the periodized payoff identity without relying on unproved pointwise convergence of a singular density.

## Strongest safe publication statement

The finite-dimensional mathematical engine and the centered packet analytic error decomposition are sound after the explicit hypotheses above are supplied. The dense binary64 postcheck soundly encloses eigenvalues. A machine tail enclosure requires the positive exact-spectrum directed backend; a machine accuracy contract additionally requires directed acceptance and preserved outer endpoint strings. The packetized, signed and noncentral floating implementations have analytic error ledgers and numerical validation, not an end-to-end directed machine enclosure. The streamed range-core/residual architecture has exact mathematical comparison theorems but is not yet a fully directed large-scale matrix-to-tail backend.

The cheapest remaining check is to run endpoint-collapse and acceptance-boundary regressions on the staged corrected source, then inspect the final serialized interval and exact acceptance predicate. Broader benchmark reruns become necessary only for changed numerical outputs or claims not already covered by those regressions.

## Commands and execution limits

Raw material was located using `rg --files`, and claim/proof neighborhoods read using `rg -n` and `sed -n`. SHA-256s were generated with standard Python `hashlib`. Attempts to run the original `mpmath` helper using both system Python and the advertised primary Python failed at import: `ModuleNotFoundError: No module named 'mpmath'`. No numerical result is inferred from that failed execution. The symbolic helper counterexample follows directly from its ambient 53-bit precision conversion; the separate numerical-validation task owns installation/execution and staged regression evidence.
