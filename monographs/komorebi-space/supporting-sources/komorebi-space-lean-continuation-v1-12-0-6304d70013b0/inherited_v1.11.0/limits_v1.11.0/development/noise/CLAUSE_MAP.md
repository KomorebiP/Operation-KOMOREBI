# WR09 and WR16 clause map

Frozen implementation: `formal/KomorebiSpace/RegularizationNoiseLimits.lean`

Source SHA-256: `8e5045c83611637d9212b9f2f3563b9bd2073c3f11fa3da67b1b7b053f5dab03`

Namespace: `KomorebiSpace.RegularizationNoiseLimits`.

## Exact printed scope

The targets are the complete named WR09 theorem in `monograph_v1.10.0/source/chapters/05h_regularized_repair.tex` and the complete named WR16 theorem in `monograph_v1.10.0/source/chapters/05k_stopping_rules.tex`. The subsequent diagonal schedule remains a separate application of WR12; it is not claimed as formalized here.

| Printed clause | Formal declaration | Correspondence |
| --- | --- | --- |
| Correction error at most `δ/(2√α)` | `noise_path_bound` | Positive parameter; actual data norm bounded by δ; same operator and spaces. Uses the accepted `data_noise_bound`. |
| Fitted-data error at most δ | `noise_fitted_path_bound` | Uses the accepted `data_fitted_bound`. |
| Sharp universal correction coefficient | `scalarSharpOperator`, `scalar_correction_formula`, `data_noise_coefficient_attained`, `data_noise_coefficient_le_of_uniform_bound` | The scalar operator `√α • id` attains equality for every scalar perturbation. Testing data 1 and 0 proves no smaller universal coefficient suffices. No claim that every fixed operator attains equality. |
| Full positive-noise-level parameter choice in WR09 | `noisy_parameter_choice_nhdsWithin` | Limit is along `𝓝[>] (0 : ℝ)`, with α positive for every positive δ, α→0, actual noise ≤δ, and δ/√α→0. No sequence restriction. |
| Attained projected datum and minimum-norm limit | `noisy_parameter_choice`, `noisy_parameter_choice_nhdsWithin` | Hypotheses identify `aMin` by `T aMin = projectedDatum T r` and minimum norm among all such preimages. The imported strong module supplies existence and uniqueness from actual range membership. No assumption `r ∈ range T`; positive residual floors are allowed. |
| Pointwise solver plus data bound | `solver_data_path_bound` | Solver certificate uses `gradient T α s a` for the measured datum s. |
| WR16 three-term bound at each index | `stopping_three_term_bound`, second conjunct of `stopping_rule_sequence` | Retains distinct ε/α, δ/(2√α), and exact-data bias terms. |
| WR16 sequence convergence | First conjunct of `stopping_rule_sequence` | Positive α at every index; α→0; δ/√α→0; ε/α→0; every data and measured normal-residual bound. Convergence is in the norm topology. |
| General filtered schedules | `noisy_tendsto_of_exact_tendsto`, `inexact_tendsto_of_exact_tendsto`, `noisy_parameter_choice`, `inexact_parameter_choice` | Supports arbitrary filters, including full real-parameter families; inequalities and positivity may hold eventually. These stronger generic forms do not replace the exact printed wrappers. |

## Hypothesis audit

- Real Hilbert spaces retain their actual norms and completeness assumptions.
- One fixed bounded linear operator is used throughout each theorem.
- No finite-dimensionality, separability, injectivity, compactness, closed range, zero floor, or changing correction space is assumed.
- The correction path is the imported total extension; every estimate uses `path_of_pos`, and all limiting wrappers ensure positivity on the relevant filter.
- The noisy and inexact limits use the independently implemented WR08 strong theorem. They do not assume a desired noisy/inexact conclusion as a premise.
- The generic transfer lemmas deliberately expose an exact-data bias limit premise; the named parameter-choice wrappers discharge it using the attained minimum-norm hypothesis and the parameter limit.
- Protection at each index is inherited by instantiating H with the protected kernel, as in the accepted protected-space construction. No asymptotic weakening of protection is introduced.

## Compilation record

The runner snapshots every source attempt and records the command, working directory, environment, imported project object hashes, source hash, exit code, elapsed time, UTC timestamp, source stability, and compiler log hash. Development reuses accepted project objects and the pinned external runtime; it is not a clean cumulative replay.

| Attempt | Result | Local issue and resolution |
| --- | --- | --- |
| 001 | Compiler rejection | Incorrect placement of symmetry on an iff-elimination function; deprecated namespaced `smul_apply` under warning-as-error; a scalar algebra goal needed substitution of `sqrt α ^ 2 = α` before ring normalization. |
| 002 | Compiler rejection | Unused simp argument under warning-as-error; the selected `norm_sub_le` was a two-vector estimate, so the desired three-vector inequality was expanded explicitly. |
| 003 | Compiler rejection | The selected additive monotonicity lemma supplied the opposite addition order; replaced with `add_le_add ... le_rfl`. |
| 004 | PASS | Full final module compiled with `-j1 -DwarningAsError=true -DautoImplicit=false`; empty compiler log. |

No theorem statement was weakened to resolve these elaboration and proof-script issues.

## Final self-review

Proofread: the entire new Lean module and its mathematical comments.

- Routine edits: none after the successful final compilation.
- Mathematical-token changes during proofreading: none.
- Unresolved local notation, quantifier, coefficient, or comment mismatch: none found.
- Validation: strict compiler attempt 004 passed; 15 explicit theorems and one public definition.
- Coverage: WR09 and WR16 named statements plus generic transfer helpers; the monograph itself was not edited, and this self-review is not an independent proof audit.
- Final cumulative declaration/axiom audit and independent exact-statement review remain integration responsibilities.
