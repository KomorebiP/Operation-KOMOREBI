# Block 11 — Strong regularization limits

Komorebi P. · Sufficient Resolution v0.11.0

## Mathematical contract

G and V are complete real inner-product spaces. A : G →L[ℝ] V is fixed and
bounded. For lambda>0, B_lambda is the ACTUAL Tikhonov map constructed in block 10:

    B_lambda = (A* A + lambda I)^(-1) A*.

For convergence, lambda is a positive family indexed by an arbitrary filter and
converges to zero. A nontrivial filter is required for converse/uniqueness claims.
No closed-range hypothesis is used for strong source convergence or noisy consistency.

## Density and an explicit approximation certificate

`TikhonovDensity.gram_range_closure` proves

    closure range(A* A) = ker(A)^perp.

`source_approximation_bound` proves, for every g,w and lambda>0,

    ||B_lambda A g - g|| <= ||g - A* A w|| + lambda ||w||.

The proof uses contraction of the bias operator and the retained source-condition
estimate. The dense normal range is established, not assumed. The source-condition
representation is used to approximate arbitrary identifiable sources; it is not
imposed on the final source.

## Strong source convergence

`TikhonovConvergence.tendsto_source` proves

    B_lambda A g --> P_ker(A)^perp g.

`tendsto_bias_vector`, `tendsto_error_norm`, `tendsto_error_squared` identify the
limits -P_ker(A)g, ||P_ker(A)g|| and its square. `exact_limit_iff_identifiable` proves
that convergence to the original g holds exactly for identifiable sources, for a
nontrivial parameter filter.

## Noise and inexact solvers

`NoisyRegularization.noisy_source_tendsto` proves consistency under

    lambda_i --> 0, lambda_i>0, ||e_i||/sqrt(lambda_i) --> 0.

The limit of B_lambda_i(A g+e_i) is P_ker(A)^perp g. The error norm retains the
kernel norm. These conditions are sufficient, not claimed necessary for every
operator or noise direction.

`noisy_inexact_solver_tendsto` additionally allows actual computed sources x_i if

    ||(A* A+lambda_i I)x_i - A*(A g+e_i)||/lambda_i --> 0.

This is the ACTUAL normal-equation residual, not a supplied claim that the source
error tends to zero. `square_schedule_consistent` supplies the explicit schedule
lambda_i=s_i^2, ||e_i||<=s_i^2, with s_i>0 and s_i-->0.

## Strong versus uniform convergence

Define E_lambda = B_lambda A - P_ker(A)^perp as an actual bounded operator.
`UniformRegularization.sourceError_norm_le_one` proves ||E_lambda||<=1.
`closed_range_of_approximate_recovery` proves that even one bounded B with

    ||B A-P_ker(A)^perp|| < 1

forces closed range. Therefore `nonclosed_sourceError_norm` proves

    range(A) not closed  ==>  ||E_lambda||=1 for EVERY lambda>0.

`uniform_convergence_iff_closed_range` proves that E_lambda converges to zero in
operator norm exactly when range(A) is closed (positive parameter tending to zero,
nontrivial filter). The positive direction retains the bound

    ||E_lambda|| <= lambda/(alpha^2+lambda)

under the supplied source coercivity alpha. This is not a claim of uniform control
across a family with vanishing alpha.

## Data-space convergence

`RegularizedDataLimit.fitted_adjoint_identity` proves the actual dual identity

    A B_lambda^A v = B_lambda^(A*) A* v.

Applying strong convergence to A* proves

    A B_lambda v --> P_closure(range A) v.

For data-space noise it is enough that e_i-->0, because the fitted-data operator
is contractive. This weaker data-space condition is not substituted into the
source-recovery theorem.

`unrealizable_no_source_limit` proves: if v belongs to closure(range A) but not
range A, its fitted data converge to v, while the reconstructed source family
cannot have a norm limit in G. No assertion of norm divergence is added.

## Boundaries

All operators are bounded, autonomous and known. Source kernel, local obstruction,
and inconsistency are distinct. Nonclosed range is never replaced by closed range
in a claim of actual source existence. Strong convergence supplies no common rate
on all identifiable sources without further hypotheses. No spectral theorem,
unbounded-generator result, nonlinear penalty, admissibility theorem or unknown-
operator learning guarantee is asserted. Tikhonov limit theory is classical; this
is a formal implementation and integration, not a novelty certificate.

The finite rational tests are bounded implementation checks, not proof of limits.
See VERIFICATION_SUMMARY.md for the actual verification scope and limitations.
