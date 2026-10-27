# Block 05 — assumption and source-admission review

**Source:** Reviewed Core 0.2, Theorem 4.1 (`r:risk`). **Status boundary:** actual proof acceptance is recorded by the current final/fresh run receipts, not by this prose checklist.

| Obligation | Formal treatment | Boundary/control |
|---|---|---|
| Same finite world set | Both distributions and response maps are functions on the same type X. | Reindexed models need an explicit correspondence first. |
| Normalized nonnegative records | Both risks use `Instrument.IsDist`; conditioning and rounding also prove this predicate. | Zero-event normalization is not a distribution. |
| Same loss | One `loss` is evaluated at both response maps. | Two different constant losses give difference one with no record/response difference. |
| Metric response scope | `PseudoMetricSpace` plus nonnegative K, pairwise sensitivity and distance bound. | A discontinuous bounded loss can have unit change at distance 1/100. |
| Bounded loss | Actual exact and approximate loss values are in [0,1]; a global source-form specialization is provided. | Unbounded losses defeat the cap and TV coefficient. |
| Both error terms | Exact finite-sum proof plus inherited TV expectation theorem. | Separate exact controls isolate each required term. |
| Action catalogue | A common finite nonempty `Finset`; selected decisions must belong to it. | No change in legal actions is inferred from a numerical bound. |
| Minima exist | Derived using finite minimum attainment; no optimum value supplied as an axiom. | Does not give an efficient extracted real optimizer. |
| Optimality vs near-optimality | Exact minimizer for the source result; separate eta theorem for optimization residual. | An intentionally poor exact-information choice has positive regret. |
| Strict gap | Every alternative has gap strictly greater than twice xi. | Equality can give a true tie; smaller gap can reverse selection. |
| Common conditioning event | P and Q are restricted to the same E; both masses positive. | Accessibility of E is a separate operational premise; sensor E is an actual report event. |
| History source | Specialized endpoints use actual `ApproximateHistory.law`, common observed-history policy, and complete joint-row defects. | No assumption that a projected process is automatically Markov. |
| Storage error | r is normalized and close to the specified approximate conditional record. | A changed retained record must pay its own discrepancy. |
| Response estimate | Uniform pointwise bound in the source; an optional expected-distance theorem weights by the declared p. | Not a data-driven estimator of that weighted expectation. |
| Risk certification | Upper/lower interval and threshold from the same xi. | Model risk is not physical safety, sure success, hard resource budget or authority. |

## Source implications actually covered

1. For every admitted action, the risk difference is at most `min(1,e+K*d)`.
2. Every approximate minimizer has true-model regret at most `min(1,2*xi)` against the attained true minimum.
3. A strict approximate gap greater than `2*xi` makes that decision the unique true minimizer.
4. The general library also provides a checked risk interval and threshold, the expected-response variant, and a separately charged approximate optimizer.
5. Generic conditional-record and actual-history composition are supporting endpoints, not extra source results added to the manuscript count.

## Concrete instance review

The example starts with the inherited eight-world prior, includes the nuisance coordinate before projecting it away, and uses the actual 37/50 and 3/4 instruments. Both observed report masses are 1/2. The stored record 19/25 is a declared normalized approximation, not an unexplained empirical estimate. Scalar losses are bounded only on the proved response range. The certificate uses xi=1/25 derived from the full conditional and storage allowances, not the smaller exact discrepancy revealed by enumeration. Decision one is selected using approximate risks; its strict true uniqueness follows through the general gap theorem.

No source mathematical statement was changed. All proof attempts that failed elaboration remain non-evidence. Kernel acceptance checks the formal implications; adequacy of the model and the user's intended semantics remains a review obligation.
