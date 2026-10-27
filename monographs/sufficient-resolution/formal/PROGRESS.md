# Progress — Sufficient Resolution v0.16.0

Komorebi P. · 14 September 2026 · Standalone program, separate from Papers I–XII.

| Inventory | v0.15.0 | v0.16.0 | Added |
|---|---:|---:|---:|
| Theorem/lemma declarations | 954 | **998** | **44** |
| Production proof modules | 87 | **93** | **6** |
| Enumerated named declarations | 1107 | **1159** | **52** |
| Predecessor proof files changed | — | **0 of 87** | Preserved |

Counts include supporting lemmas, definitions, examples and classical specializations,
not independent discoveries.

## New completed contracts

| Contract | Result |
|---|---|
| Split calibration frame | Redundant/square calibration synthesis with bounded reconstruction generates whole-operator bounds. |
| Calibration-to-operator bound | `||C-A|| <= (etaCal+fit)||R||`; exact calibration identifies the operator. |
| Calibration-to-recovery | Generated allowance feeds the existing generalized discrepancy norm-control and consistency theorems. |
| Feasibility/selection | Existing parameter-selection theorem specialized to the generated allowance and relative calibration accuracy. |
| Hierarchical calibration | Split frames compose; conditioning multiplies through the analysis maps. |
| Approximate frame | `||I-UR||<=rho<1` gives the explicit `1/(1-rho)` degradation. |
| Missing-direction boundary | Perfect calibration on a proper subspace permits arbitrarily large unseen operator error. |
| Finite companion | Exact-rational conservative calibration checker and regression suite; not formally verified Python. |

The inherited exact-resolution, behavioral-minimality, memory, obstruction, reconstruction,
regularization, discrepancy, inexact-computation, changing-operator and source-bound-free
contracts remain unchanged.

## What this block changes conceptually

Before block 16, the recovery theorems required a justified whole-operator allowance
`||C-A||<=delta`. Block 16 proves a route for **generating** such an allowance from
calibration structure:

    measured calibration truth error
      + model calibration fit
      + frame reconstruction conditioning
      -> whole-operator error allowance
      -> existing sufficient reconstruction theorem.

It also proves exactly why a nonspanning calibration family cannot provide that guarantee.

## Remaining directions

| Direction | Remaining obligation |
|---|---|
| Sample-wise uncertainty generation | Derive the calibration-operator truth allowance from finitely many noisy calibration samples and explicit frame/basis geometry. |
| Statistical calibration | Replace deterministic sample bounds by justified probabilistic confidence regions when a stochastic noise model is supplied. |
| Verified execution | Formalize the rational calibration checker, matrix bounds, parser and termination logic in Lean. |
| Practical generalized search | Verify a terminating parameter search that returns a certificate or a correct inconclusive/insufficient-model status. |
| Task-sufficient prediction | Join behavioral minimality to reconstruction so stable target predictions can be certified without full-source recovery. |
| Approximate obstruction transport | Quantify realization/compatibility square defects and induced obstruction-map errors. |
| Infinite-dimensional boundary | Formalize a fixed dense-nonclosed-range Hilbert operator and instantiate strong-vs-uniform recovery. |
| Admissible realization | Positivity, normalization, integrality, constrained/nonlinear recovery. |
| Geometry/dynamics | Moving spaces/metrics/subspaces, time-varying or unbounded generators, full Volterra converse. |
| Learning/higher realization | Unknown-operator inference, robust approximate minimality, categorical descent and domain-specific global existence. |

No whole-program completion percentage is assigned.

## Next selected target

**Sample-wise calibration certification.** For a finite calibration frame, replace the
operator-level premise `||Y-AU||<=etaCal` by finitely many per-calibration-vector error
bounds and a proved frame-conditioning constant. The target should distinguish spanning
calibration from insufficient sampling and should produce the `etaCal` used by this block
without assuming it as a whole-map input.
