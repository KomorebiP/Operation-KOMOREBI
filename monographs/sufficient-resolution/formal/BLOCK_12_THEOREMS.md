# Block 12 — Discrepancy-based regularization

**Komorebi P. · 14 September 2026 · Sufficient Resolution v0.12.0**

46 new theorem declarations, 51 named declarations, five new modules. Helpers and
classical specializations are included. No historical novelty or literature-priority
claim is made. The twelve-paper census is separate.

## Contract

Fix a bounded linear map A:G→V between complete real inner-product spaces. Use the
actual regularized recovery B_lambda=(A* A+lambda I)^(-1) A* constructed in block 10.
Only lambda>0 is admissible. Neither finite dimension nor closed range is assumed.
Let r_v(lambda)=||A B_lambda v-v||.

### Actual residual curve

`DiscrepancyResidual` proves nonnegativity, r_v<=||v||, source-norm antitonicity,
residual monotonicity, and strict residual monotonicity when A* v !=0. If A* v=0,
the curve is constant at ||v||. The equal-residual proof uses the actual unique
minimizer, not spectral assertions. A direct resolvent estimate gives

    |r_v(s)-r_v(t)| <= (||A|| ||A* v|| / a^2) |s-t|  (s,t>=a>0),

hence continuity on every compact positive parameter interval.

`recoveryAt` is a total extension set to zero at nonpositive parameters. All
selection, monotonicity and analytic contracts restrict to positive parameters.
No discontinuity across zero is hidden by the extension.

### Existence and uniqueness

`DiscrepancySelection.exists_unique_parameter_of_distance` proves

    dist(v,range A) < rho < ||v||
    ==> there exists exactly one lambda>0 with r_v(lambda)=rho.

This is actual Metric.infDist to the actual range; no closedness or realization
of a nearest point is assumed. A feasible source with residual strictly below rho
produces a positive lower bracket. The inverse-parameter estimate produces an upper
bracket. Mathlib's intermediate value theorem supplies the exact root. Strict
monotonicity supplies uniqueness. `parameter`, `parameter_pos`, and
`parameter_hits_target` construct a noncomputable real root with its specification.
`root_in_bracket` proves the soundness of any supplied positive bracket.

For a true source g, eta>0, tau>1, ||Ag-v||<=eta and ||v||>tau eta, the unique
positive root exists at rho=tau eta. These are explicit hypotheses, not estimates
of noise inferred by the theorem.

### Direct convergence, without assumed parameter asymptotics

`DiscrepancyConvergence.norm_domination_of_residual` proves that any actual Tikhonov
solution whose residual is at least that of a comparator has no larger source norm.
In particular, discrepancy selection yields

    ||x_eta|| <= ||P_(ker A)^perp g||,
    ||A x_eta-Ag|| <= (tau+1) eta.

The abstract theorem `norm_control_residual_tendsto` proves: if g is identifiable,
||x_i||<=||g||, and ||A x_i-Ag||→0, then x_i→g strongly. Its proof uses the already
proved density of range(A* A), together with the new estimate

    ||x-g||^2 <= 4||g|| ||g-A* w|| + 2||w|| ||Ax-Ag||.

Thus `discrepancy_consistent` proves strong convergence to the identifiable source
for discrepancy-selected parameters WITHOUT assuming lambda→0 or
noise/sqrt(lambda)→0. These are not relaxed claims about arbitrary choices of lambda:
the residual-selection rule replaces those assumptions.

### Small-data branch and residual bands

`DiscrepancyRule.Accepted` records either

    ||v|| <= tau eta and x=0,

or an actual positive-parameter Tikhonov solution with

    eta <= r_v(lambda) <= tau eta.

The actual map `selectedSource` returns zero on small data and otherwise the exact
root-selected solution. `selectedSource_accepted` certifies both branches.
`selectedSource_consistent` proves, for a fixed g and valid noise allowances eta_i→0,

    selectedSource(v_i,eta_i,tau) → P_(ker A)^perp g.

It uses no hand-supplied lambda schedule. The larger `Accepted` predicate permits
inexact residual targeting, but x must still be the actual Tikhonov solution at the
chosen parameter. This does NOT silently include errors in solving the normal
equation. General inexact-solver discrepancy control remains a next task.

`accepted_error_norm_limit` retains the irrecoverable ambiguity:

    ||x_i-g|| → ||P_ker(A) g||.

For the explicit source condition g=A* w, `accepted_source_rate` proves

    ||x-g||^2 <= 2 ||w|| (tau+1) eta.

No such uniform rate is claimed for all identifiable g.

### Endpoint boundaries

`DiscrepancyBoundaries` proves no root above ||v||; no positive root at ||v|| when
A* v!=0; and r_v(lambda)=0 iff v=0 for every positive lambda. Orthogonal data have
constant residual and no interior root. The identity operator has exact formulas

    lambda=rho/(v-rho),  B_lambda v=v-rho  (0<rho<v).

These demonstrate why small-data handling and a positive noise allowance matter.

## Executable companion

    python scripts/discrepancy_certificate.py --input examples/discrepancy_input.json --output certificate.json

The rational search uses only the known A, observed v, noise allowance and band
constants. It validates finite-dimensional feasibility, searches by bracketing and
bisection, and checks an exact normal equation plus squared residual inequalities.
It does not use a true source, does not take a preselected lambda, and does not
claim its rational output is the exact real root. It may return a small-data zero.

The example A=[[1,1],[0,0]], v=(4,1/10), eta=1/10 and band [3eta/2,2eta] returns
lambda=1/16, x=(64/33,64/33), residual squared 2689/108900, in five evaluations.
There is a normal-equation certificate with exactly zero residual.

Finite tests use exact Fraction arithmetic, dimensions 0..4, seed 20260914, and
eta=1/k for k=2,4,8. Python search, elimination and parsing are NOT Lean-verified.
Search caps raise errors rather than returning an uncertified success. CLI limits:
dimensions <=8, max steps <=512, input <=1 MB, inherited coefficient caps.

## Scope

This block proves existence/uniqueness of a data-selected parameter and strong
source consistency with valid known noise allowances. It does not infer the noise
level, certify unknown operators, prove the Python algorithm, provide a uniform
source convergence rate without smoothness, or establish positivity, integral,
nonlinear or arithmetic realizability. Verification scope is separately recorded.
