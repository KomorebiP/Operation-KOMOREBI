# Block 03 — source-faithful assumption review

**Target:** Reviewed Core 0.2, Theorem 5.4, canonical label `r:belief-planning`.

| Obligation | Formal location | Review conclusion |
|---|---|---|
| Fine and coarse laws are nonnegative and normalized | `Instrument.Law` | Inherited genuine joint report/next-state law, not separate marginals. |
| Exact quotient | `Intertwines`; `BeliefPlanning.instrumentMap` | Actual inherited equation is used to prove report-mass and posterior agreement. |
| Priors are probability distributions | `BeliefPlanning.Belief` | Nonnegativity and mass one are required by the subtype. |
| Positive-branch normalization | `Model.next`; `fineModel`; `coarseModel` | A positive report-mass proof is required to construct a successor belief. Impossible branches are omitted from expectations. |
| Identical actions and terminal decisions | `Contract` and `ExactMap` | Menus factor through the same retained belief. Not inferred from a quotient's probability law. |
| Nonempty finite terminal catalogue | `Model.decisions_nonempty` | Required at every information state, including horizon zero. No arbitrary minimum of an empty set. |
| Finite experiment catalogue | `Model.actions` | May be empty. Global action/decision types need not be finite when each menu is finite. |
| Finite report alphabet | `[Fintype O]` | Every possible report is included; no data-dependent truncated report enumeration. |
| Matching charges | `Contract.charge`, `ExactMap.cost` | Same finite nonnegative real charge. The changed-fee counterexample confirms necessity. |
| Matched terminal loss | `Contract.terminalLoss`, `terminal_risk_eq` | Fine loss is pulled back through pi; equality of expected loss is proved by fibre summation. |
| Horizon | `value`, `Feasible`, `Tree.Bounded` | A natural mathematical bound, not a runtime timeout. Zero horizon allows only stopping. |
| One realizable choice | `Tree`, `minimizing_tree_exists` | One experiment is chosen before its outcome. Every positive child is attached to that same node. |
| Exact minimum | `optimal_value_characterization` | Both universal lower bound and finite witness attainment are proved. |
| Actual policy transport | `ExactMap.feasible_iff`, `evaluate_eq`, `common_minimizing_tree` | Same literal tree is transported, uniformly for every fine belief in the same coarse fibre. |
| Terminal choices at zero horizon | `ExactMap.optimalStop_iff` | Explicit terminal optimality is preserved, including horizon zero. |
| Randomization boundary | `randomized_tree_lower_bound` | Finite mixtures of feasible trees cannot lower the minimum. No unrestricted randomized-policy equivalence is claimed. |
| Source sensor connection | `PlanningSensor.countMap` and `sensor_joint_quotient` | Counts are tied to actual Bayesian correction and the eight-world instrument. |
| No hidden initial-state assumption | `initialFine`, `initialFine_aggregates` | A normalized fine prior is explicitly constructed. Other priors require the stated same-aggregate hypothesis. |
| Expected work versus storage | `evaluate` | Only expected charge plus terminal loss is optimized. Syntactic finiteness is proved; storage optimality and hard budgets are not. |
| Semantic truth outside the model | Not established by the kernel | Physical calibration, learned semantics, and faithful host execution remain external premises. |

No manuscript statement required a mathematical correction. Some formal generality is greater: information-state spaces may be infinite, and only local menus need be finite. Exact real comparison and policy selection are noncomputable classical mathematical constructions, not an efficient extracted solver.

The ten inherited substantive modules remain byte-identical. Their current-source cold recompilation and local kernel replay are separate from this new source-translation review. Earlier historical receipts are not treated as current evidence without rechecking the cumulative source.
