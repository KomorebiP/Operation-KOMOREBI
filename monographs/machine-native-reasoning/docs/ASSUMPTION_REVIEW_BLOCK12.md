# Assumption and statement review — Block12

All68 newly authored theorem declarations were reviewed internally against their formal statements, source role and proofs. Kernel acceptance is a separate mandatory gate. No independent external review is claimed.

Core7.3 has two conclusions: the all-nonnegative-price equivalence and an attained minimum on the convex hull of a finite nonempty generator set. Both are proved without a changed source statement. Setup, workload, unit changes and quote replay are supporting consequences or instances, not additional selected source results.

## MachineTheory/ResourcePrices.lean

**Premises and scope.** Finite event set; exact real arithmetic; positivity, nonemptiness or unit invertibility only where stated.

**Proof mechanisms.** Finite-sum algebra, coordinate price witness, convex-halfspace closure and actual finite minimizer attainment.

| Declaration | Source line |
|---|---:|
| `Komorebi.MachineTheory.ResourcePrices.saving_zero_price` | 18 |
| `Komorebi.MachineTheory.ResourcePrices.saving_zero_events` | 21 |
| `Komorebi.MachineTheory.ResourcePrices.saving_price_add` | 24 |
| `Komorebi.MachineTheory.ResourcePrices.saving_price_smul` | 28 |
| `Komorebi.MachineTheory.ResourcePrices.saving_event_add` | 32 |
| `Komorebi.MachineTheory.ResourcePrices.saving_event_sub` | 36 |
| `Komorebi.MachineTheory.ResourcePrices.saving_event_smul` | 40 |
| `Komorebi.MachineTheory.ResourcePrices.all_nonnegative_prices_iff` | 49 |
| `Komorebi.MachineTheory.ResourcePrices.adverse_price_of_negative` | 60 |
| `Komorebi.MachineTheory.ResourcePrices.not_strict_at_all_nonnegative_prices` | 68 |
| `Komorebi.MachineTheory.ResourcePrices.lower_halfspace_convex` | 75 |
| `Komorebi.MachineTheory.ResourcePrices.hull_lower_bound_iff` | 86 |
| `Komorebi.MachineTheory.ResourcePrices.finite_price_minimum` | 95 |
| `Komorebi.MachineTheory.ResourcePrices.listed_hull_minimizer` | 108 |
| `Komorebi.MachineTheory.ResourcePrices.consistent_unit_change` | 118 |
| `Komorebi.MachineTheory.ResourcePrices.rescaled_price_nonnegative` | 126 |

## MachineTheory/WorkloadPricing.lean

**Premises and scope.** Natural workload/count data, one common additive price vector; strict positive per-use margin for division threshold.

**Proof mechanisms.** Cast before subtraction, interchange finite sums, monotonicity and ordered-field arithmetic.

| Declaration | Source line |
|---|---:|
| `Komorebi.MachineTheory.ResourcePrices.Ledger.delta_eq_total_difference` | 38 |
| `Komorebi.MachineTheory.ResourcePrices.saving_net` | 45 |
| `Komorebi.MachineTheory.ResourcePrices.Ledger.saving_eq_cost_difference` | 59 |
| `Komorebi.MachineTheory.ResourcePrices.workload_robust_iff` | 68 |
| `Komorebi.MachineTheory.ResourcePrices.saving_mono` | 76 |
| `Komorebi.MachineTheory.ResourcePrices.preparation_is_not_free` | 80 |
| `Komorebi.MachineTheory.ResourcePrices.saving_repeated` | 91 |
| `Komorebi.MachineTheory.ResourcePrices.amortization_iff` | 97 |
| `Komorebi.MachineTheory.ResourcePrices.no_amortization_of_nonpositive` | 103 |
| `Komorebi.MachineTheory.ResourcePrices.robust_repeated_lower` | 111 |
| `Komorebi.MachineTheory.ResourcePrices.workload_minimum` | 118 |

## MachineTheory/PriceExamples.lean

**Premises and scope.** Inherited exact compiler semantics and counters; fixed workload; declared convex price family; setup200 is hypothetical.

**Proof mechanisms.** Projection of inherited proof terms, exact arithmetic, actual-hull minimum and all-N induction-free algebra.

| Declaration | Source line |
|---|---:|
| `Komorebi.MachineTheory.PriceExamples.counter_binding` | 26 |
| `Komorebi.MachineTheory.PriceExamples.actual_delta` | 32 |
| `Komorebi.MachineTheory.PriceExamples.priced_scan` | 38 |
| `Komorebi.MachineTheory.PriceExamples.same_valid_controller` | 43 |
| `Komorebi.MachineTheory.PriceExamples.source_price_reversal` | 48 |
| `Komorebi.MachineTheory.PriceExamples.not_universally_beneficial` | 51 |
| `Komorebi.MachineTheory.PriceExamples.natural_subtraction_loses_cost` | 59 |
| `Komorebi.MachineTheory.PriceExamples.expensive_nonempty` | 69 |
| `Komorebi.MachineTheory.PriceExamples.listed_minimum` | 73 |
| `Komorebi.MachineTheory.PriceExamples.expensive_hull_minimum` | 87 |
| `Komorebi.MachineTheory.PriceExamples.equal_price_outside_family` | 93 |
| `Komorebi.MachineTheory.PriceExamples.preparation_price` | 105 |
| `Komorebi.MachineTheory.PriceExamples.actual_workload_delta` | 116 |
| `Komorebi.MachineTheory.PriceExamples.actual_workload_totals` | 120 |
| `Komorebi.MachineTheory.PriceExamples.time_varying_prices_boundary` | 129 |
| `Komorebi.MachineTheory.PriceExamples.paid_value` | 132 |
| `Komorebi.MachineTheory.PriceExamples.paid_at_five` | 137 |
| `Komorebi.MachineTheory.PriceExamples.paid_strict_threshold` | 141 |
| `Komorebi.MachineTheory.PriceExamples.paid_hull_minimum` | 152 |
| `Komorebi.MachineTheory.PriceExamples.robust_reuse_threshold` | 170 |
| `Komorebi.MachineTheory.PriceExamples.setup_and_boundary_values` | 183 |
| `Komorebi.MachineTheory.PriceExamples.equal_price_never_pays` | 191 |
| `Komorebi.MachineTheory.PriceExamples.workload_change_boundary` | 197 |
| `Komorebi.MachineTheory.PriceExamples.negative_price_boundary` | 203 |
| `Komorebi.MachineTheory.PriceExamples.extrapolation_boundary` | 207 |
| `Komorebi.MachineTheory.PriceExamples.unmatched_units_boundary` | 212 |
| `Komorebi.MachineTheory.PriceExamples.source_ledger_arithmetic` | 220 |

## MachineTheory/PriceRevision.lean

**Premises and scope.** Fixed finite dependency/checker system, old established witnesses, actual immutable compiler and exact quote values.

**Proof mechanisms.** Complete-dependency proof, finite replay equations and inherited soundness at every stage.

| Declaration | Source line |
|---|---:|
| `Komorebi.MachineTheory.PriceRevision.actualSaving_eq` | 22 |
| `Komorebi.MachineTheory.PriceRevision.actualSaving_real` | 28 |
| `Komorebi.MachineTheory.PriceRevision.rank_checked` | 41 |
| `Komorebi.MachineTheory.PriceRevision.meanings_complete` | 75 |
| `Komorebi.MachineTheory.PriceRevision.old_checks` | 103 |
| `Komorebi.MachineTheory.PriceRevision.old_established` | 107 |
| `Komorebi.MachineTheory.PriceRevision.reprice_propagates` | 110 |
| `Komorebi.MachineTheory.PriceRevision.stale_quote_outcomes` | 120 |
| `Komorebi.MachineTheory.PriceRevision.corrected_quote_outcomes` | 125 |
| `Komorebi.MachineTheory.PriceRevision.every_stage_sound` | 130 |
| `Komorebi.MachineTheory.PriceRevision.restored_calculation` | 135 |
| `Komorebi.MachineTheory.PriceRevision.benefit_now_false` | 142 |
| `Komorebi.MachineTheory.PriceRevision.execution_certificate_reused` | 147 |
| `Komorebi.MachineTheory.PriceRevision.restored_negative_real_saving` | 155 |

## Additional boundary review

The cone theorem includes the zero price, so the conclusion is nonnegative rather than strictly positive. The convex theorem uses a nonempty finite set for attainment, not an arbitrary chosen price or only one favorable endpoint. Arithmetic division is restricted to a positive per-use margin. Signed savings are formed after casting, not by natural subtraction. AllN repetition theorems use the same per-use event vector. Fixed common prices are distinct from varying prices between uses. Unit conversions affect both events and prices. The repricing graph is proved complete for the exact supplied data family; it does not claim to discover a dependency graph. Correct valuation and benefit are separate propositions.

The exact counterexample fixtures in `checks/negative/Prices*.lean` must fail for the specified mathematical diagnostic. They are not production proof placeholders. Twelve new fixtures passed their first diagnostic rehearsal; actual cumulative outcomes belong to the completed current-source gates.
