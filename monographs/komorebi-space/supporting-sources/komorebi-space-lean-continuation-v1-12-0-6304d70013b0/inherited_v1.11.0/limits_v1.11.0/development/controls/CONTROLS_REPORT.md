# WR08 / WR09 / WR16 control development record

Status: all four positive controls compile with no warnings; all five negative controls fail at exactly the intended type mismatch. Integrated clean replay remains the acceptance gate.

The positive controls exercise the full positive-parameter filter, arbitrary filtered parameter choices, a positive residual floor for the zero operator, unique minimum preimage construction and strong convergence, escape beyond each finite budget, independent scaled noise and solver tolerances, the three-term pointwise certificate, and the exact sharp scalar coefficient.

The negative controls mutate a mathematical hypothesis or conclusion: strict positivity becomes nonnegativity; the right-hand parameter filter becomes two-sided; actual range membership becomes closure membership; delta/sqrt(alpha) decay becomes delta decay; epsilon/alpha decay becomes epsilon decay. Each rejection has a manifest of precise expected diagnostic substrings. They do not use unrelated false goals or missing imports as a substitute for rejecting the intended mutation.

Every development attempt retains the exact source snapshot, command, working directory, relevant environment, imported project-object hashes, exit code, timing, log, and hashes. The accepted v1.10.0 project objects are read-only symlink dependencies in an isolated development build; only new module objects are copied from author builds. This is development evidence, not a substitute for the clean integration replay.

## Development corrections

- Attempts 001 and 004: a positive zero-operator proof triggered the unnecessarySimpa linter. The final proof uses the new residual-limit theorem and an explicit projection computation.
- Attempt 006: the zero minimum-norm comparison needed the explicit norm_zero rewrite.
- Attempt 011: the scalar norm lemma is norm_one, not Real.norm_one; corrected without changing the statement.
- Attempts 002 and 010 remain as superseded controls. The positivity negative was strengthened to use the identity operator, where the zero-parameter mutation is actually false. The noisy/inexact positive was strengthened to call the complete parameter-choice theorems from minimum-preimage hypotheses, rather than assuming an exact-data bias limit.

No production theorem, root ledger, accepted historical source, or compiler policy was changed by this control task.

## Current control evidence

| Control | Kind | Final development attempt | Result |
|---|---|---|---|
| `positive/FullPositiveParameterLimits.lean` | positive | `attempt_005` | PASS |
| `positive/MinimumNormAndEscape.lean` | positive | `attempt_008` | PASS |
| `positive/NoisyAndInexactFilters.lean` | positive | `attempt_015` | PASS |
| `positive/SharpNoiseCoefficient.lean` | positive | `attempt_014` | PASS |
| `negative/NonpositiveParameter.lean` | negative | `attempt_009` | PASS |
| `negative/TwoSidedParameterLimit.lean` | negative | `attempt_003` | PASS |
| `negative/ClosureIsNotAttainment.lean` | negative | `attempt_007` | PASS |
| `negative/NoiseDecayWithoutScaling.lean` | negative | `attempt_012` | PASS |
| `negative/SolverDecayWithoutScaling.lean` | negative | `attempt_013` | PASS |
