# Block 10 — Regularized reconstruction

**Komorebi P. · v0.10.0 · 13 September 2026, America/Chicago**

This block adds 83 theorem declarations and seven production proof modules. The
cumulative source census is 728 theorems and 863 explicitly named declarations in
60 modules. Counts include helpers, classical specializations and exact examples.
The Papers I–XII census is not changed. See VERIFICATION_SUMMARY.md for actual run status.

## Contract

`G,V` are complete real inner-product spaces. `A : G →L[ℝ] V` is an actual bounded
operator and `lam > 0`. Neither finite dimension, closed range of A, a supplied
inverse, nor a fixed-rank assumption is needed for the core regularized construction.

Write N_lambda = A* A + lambda I, R_lambda = N_lambda^{-1},
B_lambda = R_lambda A*. All three are actual continuous linear maps. The
source-comparison/globalization module explicitly reinstates closed range only when
using the predecessor's Moore–Penrose inverse or harmonic quotient geometry.

## 1. Construction — TikhonovConstruction.lean

`normalForm_coercive` proves coercivity of the actual normal form. Mathlib's
Lax–Milgram theorem supplies `normalEquiv`; `normalEquiv_apply` identifies its map
with A* A + lambda I. `resolvent` is the continuous inverse of this equivalence.
`normal_resolvent`, `resolvent_normal`, `normal_injective`, and `normal_surjective`
prove both inverse laws and bijectivity. `regularized` is then R_lambda A*.

Principal contracts:

    N_lambda B_lambda v = A* v
    A*(A B_lambda v - v) + lambda B_lambda v = 0
    ||A B_lambda v||^2 + lambda ||B_lambda v||^2 = <v, A B_lambda v>

The solution is not defined as an assumed minimizer.

## 2. Actual objective and uniqueness — TikhonovOptimality.lean

The objective is the literal expression

    F_lambda(v,x) = ||A x-v||^2 + lambda ||x||^2.

For x_lambda = B_lambda v, `objective_increment` and `objective_gap` prove

    F_lambda(v,x) = F_lambda(v,x_lambda)
        + ||A(x-x_lambda)||^2 + lambda ||x-x_lambda||^2.

`unique_minimizer`, `normal_iff_minimizer`, and `exists_unique_minimizer` establish
that the normal equation is equivalent to being the unique global minimizer.
Strict positivity of lambda is retained. `source_objective_certificate` bounds
source error by the actual objective gap.

## 3. Sharp fixed-parameter bounds — TikhonovBounds.lean

For every x and v:

    ||R_lambda x|| <= ||x||/lambda
    ||R_lambda|| <= 1/lambda
    4 lambda ||B_lambda v||^2 <= ||v||^2
    ||B_lambda v|| <= ||v||/(2 sqrt(lambda))
    ||B_lambda|| <= 1/(2 sqrt(lambda))
    ||A B_lambda v|| <= ||v||
    ||A B_lambda v-v|| <= ||v||.

`approximate_solver_identity` and `approximate_solver_bound` provide the exact
normal-residual certificate for an arbitrary computed source x:

    x-B_lambda v = R_lambda(N_lambda x-A* v)
    ||x-B_lambda v|| <= ||N_lambda x-A* v||/lambda.

`source_kernel_orthogonal` proves that the selected source lies in ker(A)^perp.
Data in range(A)^perp are ignored even without a closed-range assumption on A.
The constants concern whole maps and are not inferred from samples.

## 4. Bias, noise, and invisible source content — TikhonovBias.lean

`filter_decomposition` and `noisy_error_identity` give

    B_lambda A g + lambda R_lambda g = g
    B_lambda(A g+e)-g = -lambda R_lambda g + B_lambda e.

Let p=P_ker(A)^perp g and k=P_ker(A) g. The exact theorem
`noisy_source_error_squared` is

    ||B_lambda(A g+e)-g||^2
      = ||-lambda R_lambda p + B_lambda e||^2 + ||k||^2.

Bias and propagated noise are NOT assumed orthogonal. Only their combined
identifiable error is orthogonal to k.

For an explicit source-conditioning constant alpha>0 satisfying
alpha ||x|| <= ||A x|| on ker(A)^perp, `full_conditioned_error_squared` proves

    ||B_lambda(A g+e)-g||^2
      <= (lambda/(alpha^2+lambda) ||p||
            + ||e||/(2 sqrt(lambda)))^2 + ||k||^2.

This alpha belongs to A, not to the compatibility map delta.

`source_filter_bound` proves ||B_lambda A g|| <= ||g||. The source-condition theorem
requires g=A* A w and establishes

    ||B_lambda A g-g|| <= lambda ||w||
    ||B_lambda(A g+e)-g|| <= lambda ||w|| + ||e||/(2 sqrt(lambda)).

This source-condition rate needs no closed range of A. It is not a theorem that
all identifiable sources have such a w with controlled norm.

## 5. Parameter and changing-operator sensitivity — TikhonovPerturbation.lean

For a second bounded operator C, define its corresponding normal operator and
resolvent. `resolvent_difference` is the actual two-operator/two-parameter identity

    R_A,lambda - R_C,mu
       = R_A,lambda (N_C,mu-N_A,lambda) R_C,mu.

Consequently,

    ||R_A,lambda-R_C,mu|| <= ||N_C,mu-N_A,lambda||/(lambda mu).

At a fixed positive lambda, with eta=||A-C||,

    ||B_A,lambda-B_C,lambda||
      <= eta/lambda
          + (||A||+||C||) eta ||C||/lambda^2.

This estimate allows rank changes and has no lower-singular-value assumption.
It is not uniform as lambda tends to zero. The operator norms remain explicit.

For fixed A:

    R_lambda x-R_mu x = (mu-lambda) R_lambda R_mu x
    ||R_lambda x-R_mu x|| <= |mu-lambda| ||x||/(lambda mu).

## 6. Integration with intrinsic globalization — TikhonovGlobalization.lean

Under the predecessor's complete/closed actual range hypothesis, let B=A-dagger.
Then

    B_lambda v = B_lambda A Bv
    B_lambda v-Bv = -lambda R_lambda Bv
    ||B_lambda v|| <= ||Bv||.

With source coercivity alpha,

    ||B_lambda v-Bv|| <= lambda/(alpha^2+lambda) ||Bv||.

`regularized_equals_pseudoinverse_iff` and `regularized_best_image_iff` prove that
positive regularization agrees exactly with the unregularized best source/image
only when Bv=0. Otherwise some fitting bias is deliberately introduced.

For delta A=0, let c(v) be the EXISTING projected obstruction class, equipped with
its native quotient norm, and let i(v) be inconsistency. Then

    ||v-A B_lambda v||^2
       = ||c(v)||^2 + ||i(v)||^2 + ||A(B_lambda v-Bv)||^2.

The literal objective for any g decomposes as

    F_lambda(v,g) = ||c(v)||^2 + ||i(v)||^2
                     + ||A(g-Bv)||^2 + lambda ||g||^2.

Regularization does not remove the irreducible obstruction or inconsistency.

## 7. Actual scalar examples — TikhonovExamples.lean

For A_c(x)=cx, the constructed map is proved to satisfy

    B_lambda(v) = c v/(c^2+lambda).

For c=r>0 and lambda=r^2:

    B_lambda(v)=v/(2r),
    4 lambda ||B_lambda(v)||^2=||v||^2,
    B_lambda(A_c(1))=1/2.

Thus the noise bound is attained. Arbitrarily small data can reconstruct to one
when lambda is also allowed to vanish. The zero forward map cannot recover the
source 1. An explicit lambda=0 example has nonunique objective minimizers.

## Executable example

    python scripts/tikhonov_certificate.py --input examples/tikhonov_input.json --output certificate.json

For A(g1,g2)=(g1+g2,0,0), v=(3,4,5), and lambda=1:

    regularized source = (1,1)
    unregularized minimum-norm source = (3/2,3/2)
    regularized fitting error squared = 42 = 16+25+1
    regularized objective = 44
    unregularized source's penalized objective = 91/2.

The 16 and 25 terms are existing obstruction and inconsistency. The extra 1 is
regularization image bias. The rational example is tested Python, not a separately
kernel-checked matrix example. Universal Lean contracts are independent of it.

## Boundaries and attribution

Tikhonov regularization, adjoints and Lax–Milgram are classical mathematics. This
block implements and integrates them with the preceding sufficient-resolution,
source-ambiguity and intrinsic-obstruction contracts. It is not a novelty certificate.
No positivity-constrained inverse, nonlinear regularization, parameter-choice rule,
unknown-operator inference, spectral-truncation algorithm or general strong-limit
convergence theorem is claimed. Small lambda alone does not imply uniform stability.
