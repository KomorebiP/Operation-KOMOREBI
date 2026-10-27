# WR03 profile geometry development record

Base checkpoint: KS-v1.9.0-full-monograph-proofread.

Owned production file: `formal/KomorebiSpace/BudgetProfileGeometry.lean`.
Source SHA-256: `edee3c011c62ef35c044fa5fe415a493ab6c0ff960970e7d7af72a71113757c6`.

## Exact clause map

All declarations are in `KomorebiSpace.BudgetProfileGeometry`. The profile is the shared `KomorebiSpace.BudgetProfile.beta`, defined by the distance to the actual closed correction ball's image.

| Printed clause | Declaration | Scope |
| --- | --- | --- |
| Nonincreasing on nonnegative budgets | `beta_antitone` | `0 ≤ M₁`, `M₁ ≤ M₂` imply `beta T r M₂ ≤ beta T r M₁` |
| Zero budget | `beta_zero` | `beta T r 0 = ‖r‖` |
| Convexity | `beta_convex_combination` | Every `M₁,M₂ ≥ 0`, every `t ∈ [0,1]`, with the exact printed convex-combination inequality |
| Feasible radial shrink and displacement | `radial_shrink_bounds` | For `0 ≤ M₁ ≤ M₂`, `M₂ > 0`, `‖a‖ ≤ M₂`, both printed norm bounds hold |
| One-sided Lipschitz estimate | `beta_sub_le` | Every `0 ≤ M₁ ≤ M₂`, including `M₂ = 0` |
| Combined two-sided bound | `beta_profile_bounds` | `0 ≤ beta M₁ - beta M₂ ≤ ‖T‖ * (M₂-M₁)` as a conjunction |

The profile theorems have the target's complete real Hilbert source and target, an arbitrary continuous linear map, and arbitrary datum. No finite-dimensionality, separability, closed-range, or injectivity assumption was added. The radial helper omits completeness because it only uses norm geometry. Convexity is stated as the full parameter inequality rather than packaged as `ConvexOn`.

## Proof mechanism

Monotonicity evaluates the larger-budget infimum at a smaller-budget minimizer. Convexity takes the convex combination of two attained minimizers and applies the triangle inequality to the combined residual. The quantitative bound radially shrinks a larger-budget minimizer and bounds the residual displacement with the operator norm. The case `M₂ = 0` is separate and reduces to equality, avoiding division by zero.

## Attempts and corrections

- Attempt 001 failed compilation. The radial helper inherited an unused `CompleteSpace H` parameter, which triggers the enabled linter. Two uses of `add_le_add_left` had the wrong additive orientation. The parameter was explicitly omitted and the inequalities were replaced by `add_le_add (le_refl _) ...`.
- Attempt 002 failed parsing because the documentation comment preceded `omit`. Moving `omit ... in` before the documentation comment corrected the declaration syntax.
- Attempt 003 passed, with an empty compiler log, `-j1 -DwarningAsError=true -DautoImplicit=false`. The source was unchanged during compilation. The numbered attempt directories preserve every exact source, log, command, environment, and receipt.
- One preliminary read command asked for `records/TARGET_CONTRACT.md`; the actual file is `TARGET_CONTRACT.md` at the work-package root. This was an inspection-path error only and caused no source changes.

No mathematical counterexample or failure of the chosen proof route occurred. All corrections above are recorded as failures rather than silently discarded.

## Verification boundary

This is development compilation against the shared BudgetProfile API, plus accepted predecessor objects and pinned Mathlib caches. The base API was compiled in the owner's attempt 002 before this module's successful attempt. The shared base may subsequently grow while preserving its API. A final frozen integrated replay, complete axiom audit, independent type review, and parent-owned boundary controls remain required before release acceptance. This report does not certify those steps or WR03's remaining floor and limit clauses.
