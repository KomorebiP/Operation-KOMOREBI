# Block 14 — uncertain forward operators

Komorebi P. · 14 September 2026 · Sufficient Resolution v0.14.0

49 theorem/lemma declarations and 52 enumerated names in six new modules. The
864-theorem/75-module/1010-name v0.13.0 checkpoint is the selected predecessor.
The cumulative inventory is 913 theorems, 81 modules, 1062 named declarations.
Counts include lemmas, classical specializations and examples, not novelty claims.
Verification status is recorded in VERIFICATION_SUMMARY.md, not inferred from this guide.

## Contract

A:G→V is the fixed true bounded linear operator between real Hilbert spaces.
C_i:G→V are available bounded operators on the same normed spaces. Set
p=P_(ker A)^perp g. Assume true bounds

    ||C_i-A|| <= delta_i,  ||Ag-v_i|| <= eta_i,  ||p|| <= M.

The supplied M is fixed. The effective model noise is

    epsilon_i = eta_i + delta_i M.

The error allowances are mathematical premises. A residual-only computation does
not establish them. Finite dimension, closed range, equal ranks, agreement of
kernels, and convergence of kernel projections are not assumed.

## 1. Effective data noise and observable error

`OperatorUncertainty.effective_data_noise` proves ||C p-v||<=eta+delta M.
The module also proves whole-vector forward errors, the fitting-norm difference
<=delta||x||, an observed-residual enclosure transferred to the true operator,
and ||A||<=||C||+delta. Its elementary bounds work for normed spaces; the main
regularization theorems use real Hilbert spaces.

`OperatorResidualTransport.normal_residual_difference` proves the exact identity

    r_A-r_C = (A*-C*)(Cx-v) + A*(A-C)x,
    r_D = (D*D+lambda I)x-D*v.

The available-operator bound is

    ||r_A-r_C|| <= delta (||Cx-v|| + (||C||+delta)||x||).

Thus an imperfect solve and an imperfect model are not confused. The algebraic
identity and bound do not require lambda>0; inversion/certificates do.

## 2. Accepted exact companions under changing models

An `Accepted C v epsilon tau y` is the EXISTING discrepancy predicate: y=0 in
the small-data branch or y is an actual positive-parameter Tikhonov solution with
residual in [epsilon,tau epsilon]. In the ordinary selector tau>1 and epsilon>0.

The checked estimates are

    ||y|| <= ||p||,
    ||Ay-Ap|| <= (tau+1)(eta+delta M).

The key point is norm domination by the FIXED limiting source p. No uniform
estimate for an inverse or agreement of model kernels is used.

For `NearAccepted C ... kappa x`, the inherited predicate supplies an accepted
exact companion y with ||x-y||<=kappa. Then

    ||x|| <= ||p||+kappa,
    ||Ax-Ap|| <= ||A|| kappa + (tau+1)(eta+delta M).

Under p=A*w, the squared source rate is

    ||x-p||^2 <= 2 kappa^2 + 4||w||(tau+1)(eta+delta M).

This rate has an explicit source condition, not a universal convergence rate.

## 3. Strong source convergence

`ChangingConsistency.projected_consistent` proves, for arbitrary filter-indexed
families with the above allowances and near-accepted outputs,

    eta_i -> 0, delta_i -> 0, kappa_i -> 0  ==>  x_i -> p.

The theorem does NOT assume lambda_i->0, eta_i/sqrt(lambda_i)->0, or
operator_error/lambda_i->0. The acceptance/margin hypotheses remain essential.

It also proves ||x_i-g|| -> ||P_(ker A)g|| and P_(ker A)x_i -> 0. The kernel here
belongs to the true fixed A, not to C_i. The latter projected leak is a limit,
not a finite bound by kappa_i (the exact companion may lie outside ker(A)^perp).

## 4. Operational certificates and actual parameter selection

`OperatorCertificates.Certified` uses C, observed v, eta, delta, M, tau, kappa
and either a small-data source bound or the EXISTING squared PositiveCertificate
with effective noise eta+delta M. It does not contain the unknown true A.

`certified_consistent` transfers these actual finite records into the strong
convergence theorem under the external true bounds. `inflated_feasibility` derives
model-data feasibility from those bounds; it is not supplied without a proof.
`selected_from_allowances_consistent` applies the existing total discrepancy
selector using that derived feasibility. Selection of the exact real parameter
is noncomputable, not an extracted numerical algorithm.

## 5. Actual examples and boundaries

The fully checked scalar certificate has

    true A=11/10, available C=1, true g=4, observed v=22/5,
    eta=1/10, delta=1/10, M=4, effective noise=1/2,
    lambda=1/3, computed x=331/100, kappa=1/25,
    normal envelope=1/75, image budget=1/50,
    measured fit=11/10, measurement uncertainty=1/100, tau=3.

The model's exact source is 33/10, so x is genuinely inexact. The normal residual
is 1/75. The true operator and data allowances are separately checked in Lean.

The scalar inflation eta+delta M is sharp. With fixed positive operator error,
no bound on induced data error independent of source size is possible.

The persistent-bias counterexample has true A=1, true g=v=1, available C=2.
For 0<s<1, lambda=4s/(1-s) yields an exact accepted model source (1-s)/2 and
model residual s. As s->0, these sources tend to 1/2, not 1. The vanishing
operator-error hypothesis is violated: ||C-A||=1. This is an intended boundary,
not a contradiction of the consistency theorem.

A kernel example shows nonzero scalar operators have zero kernel while their
zero-operator limit has the whole-space kernel. The accepted zero-data rule
still works; the general theorem does not require kernel agreement.

## Executable companion

    python scripts/uncertain_operator_certificate.py --input examples/uncertain_operator_input.json --output certificate.json
    python scripts/check_operator_uncertainty.py

The wrapper uses the prior inverse-free rational checker with the effective
allowance. It deliberately never receives A or the true source. The output
labels operator/noise/source bounds as externally required, not verified.

75 finite systems, source/target dimensions 0..4, seed 20260914. 956 rational
assertions, 18 rank-change cases, 344 rejected malformed/corrupted controls,
eight separate SymPy comparisons. These are bounded implementation checks,
not the universal limit proofs or formally verified algorithms.

## Remaining boundaries

No inference of eta, delta, or M from finite fitting data. No operator-dependent
uniform convergence over all sources. No varying ambient spaces/metrics,
nonlinear dynamics, positive/integral/arithmetic existence, or formal verification
of Python. Source ambiguity is always ker(A), not the changing model kernel.
