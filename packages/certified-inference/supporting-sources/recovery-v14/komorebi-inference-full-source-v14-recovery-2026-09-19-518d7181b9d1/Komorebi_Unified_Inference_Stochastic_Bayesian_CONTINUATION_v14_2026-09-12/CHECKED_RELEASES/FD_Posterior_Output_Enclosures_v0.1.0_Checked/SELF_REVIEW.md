# Adversarial self-review

Primary verdict for the new universal output contract: proved as written. The final receipt
records 82 compiled modules and complete axiom coverage of 416 declarations.
This is a self-review and fresh local reproduction, not an independent human or
fresh-agent audit of the entire historical mathematical program.

| Obligation | Verdict | Evidence |
|---|---|---|
| Exact finite rational input and two positive tolerances | Passed | run_terminates signature; run rejects nonpositive delta |
| Actual graph includes every specified rounded operation | Passed | PosteriorOutput definitions and budget composition |
| Covariance is valid for arbitrary gain, including singular prior | Passed | outputCovariance_posSemidef via retained Joseph PSD theorem |
| Arrays enclose the parameters of the certified law | Passed | approximation_eq_output_gaussian plus evaluate_encloses |
| All returned radii meet delta, without assuming a good precision | Passed | computed outputPrecision and represent_spec |
| Actual program returns these arrays and same candidate | Passed | run_terminates, run_sound, ResultValid evaluator equality |
| Empty finite types handled by universal sums | Passed | no nonempty assumptions in new universal statements |
| Covariance centers may be used as a valid new covariance | Refuted | rank-one input, vector (-3,1), negative form -1 after rounding |
| Python values correspond to evaluated arrays in two examples | Passed when final examples compile | explicit field equalities in GeneratedOutputScalar/Rotated |
| Universal parser/exporter, finite-word or sampling correctness | Out of scope | unchanged boundary; Python success remains provisional |
| Numerical code is independent evidence | Bounded only | direct factor-sum reference, six cases, exact arithmetic |
| Literature novelty or practical advantage | Not addressed | no such claim in this release |

The dependency graph for the added claim is:
retained dyadic ball soundness and budget rules -> output graph bounds -> computed
precision sufficiency -> represented array guarantee; retained rational model
semantics and Joseph PSD -> law identity; both branches plus retained rounded
solver successful termination -> combined program theorem.

No new external mathematical source is invoked. Existing internal theorem sources
in the active slice were freshly compiled under the pinned mathlib/runtime.
The meaning of the existing posterior definition and its documented explicit
version boundary are preserved, not broadened by this review.

Final mathematical proofreading covers new Lean statements, PROOF_NOTE.md,
README.md and continuation text. The two tolerances and output-law convention are
consistent. No substantive mathematical correction was made by proofreading.
