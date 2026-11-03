# Focused self-review: analytic uniqueness and the F.1 contract

Primary verdict: **proved as written**, for the exact ordinary-series F.1
contract and the local/global uniqueness interfaces stated here. Review
provenance: self-review.

Claim card: for fixed labeled real scales in `(0,1)`, there is a unique
normalized entire solution pair. Every normalized analytic solution germ is
the canonical germ and has its positive odd recurrence-series expansion near
zero. Entire solutions have that expansion everywhere and are odd. The
competing functions are not assumed odd or given coefficient formulas.

The generic conditional uniqueness lemmas allow arbitrary real scales and
equal initial values. The canonical entire existence and series bridge use
the manuscript's strict positive contraction hypotheses. The exact reviewed
source is bound by `declarations.json` and the execution receipt; the base is
`b479654cc33423e56e3dd81cd1f63f9e19efcf84`.

Dependency graph:

`analytic differences + equal initial values + local equations →`
`derivative difference identities → vanishing-order induction → germ equality →`
`global analytic identity for entire solutions → entire uniqueness`.

`entire uniqueness + Block03 existence → unique normalized pair`;
`germ identification + Block03 convergence + Block01 recurrence/positivity →`
`canonical HasSum expansions and the ordinary-series F.1 bundle`.

| Obligation | Assessment |
|---|---|
| Arbitrary competing functions | Passed: only analyticity, initial values and the coupled equations are inputs. |
| Actual derivatives | Passed: entire solutions use `HasDerivAt`; germ equations are used with analytic-at-zero hypotheses. |
| Output/input alignment | Passed: the derivative-difference helper separates output functions from the two product factors, so the V row still uses f(a*z)*g(b*z). |
| Initial-value role | Passed: both differences vanish at zero before invoking the derivative-order increment. |
| Scaling | Passed: nonzero scales preserve order via an invertible linear map; zero scaling makes a zero difference identically zero. |
| Product and sum orders | Passed: analytic factors preserve lower bounds and the order of a sum is bounded below by the minimum. |
| Induction base and step | Passed: order at least zero is automatic; the step proves the successor bound for both components simultaneously. |
| Infinite-order implication | Passed: all finite bounds give top analytic order and local zero germs. |
| Local versus global | Passed: the identity theorem is used only after entire solutions provide global analyticity. |
| Coefficient normalization | Passed: index n multiplies z^(2*n+1), so index zero is the coefficient one of z. |
| Reverse bridge | Passed in its explicit HasSum form; no parity or recurrence premise is imposed on the competitor. |
| F.1 coverage | Passed: unique normalized pair, the constructed recurrence, strict coefficient positivity, expansions everywhere and oddness are all in the bundle. |
| Parameter inverse | Out of scope: uniqueness fixes s throughout; cross-parameter germ-to-jet extraction remains open. |
| Arbitrary supplied Taylor-series object | Out of scope: its coefficient-vector transport is not asserted by this block. |

At the smallest order, equality of initial values supplies the first vanishing
bound. With all scales zero, the normalized equations reduce to derivatives
one, and the positive fixture identifies every entire solution pair with
`(id,id)`. Zero functions have the right initial values but the wrong
derivatives, so they are rejected. Nonzero origin values are rejected by the
solution predicate.

External leaves are the pinned Mathlib vanishing-order scaling, product, sum,
derivative increment, infinite-order characterization, and analytic identity
theorems. Their exact typed hypotheses are discharged in Lean. No sample or
approximate computation substitutes for a universal argument. The command
logs and axiom inventories are in `evidence/` with their SHA-256 bindings.

The strongest safe statement is the ordinary-series F.1 contract and the
canonical series representation of arbitrary solution germs. The next missing
implication is equality of finite jets from equality of canonical analytic
germs, with the factorial normalization respected if derivatives are used.
That implication, followed by Block01's guarded inverse, is the next check.
