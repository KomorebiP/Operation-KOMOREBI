# Development record

This record distinguishes setup failures from mathematical outcomes.

* The first bounded-run invocation for the unit15 discriminator omitted
  explicit runner input pins. The runner rejected it before execution.
  The corrected invocation pinned all six code/data inputs, completed,
  and validated. Its result is independently replayed in `../review/`.
* A shell cleanup command for an unused helper directory was automatically
  rejected because its deletion form was disallowed. No helper was removed
  and no mathematical work was affected. A fresh private directory was
  created instead, with no deletion needed.
* No new Lean compilation was attempted.
* The mathematical failures are recorded in the individual route proofs,
  especially the false parity/unit exclusion, the failed orthogonal-remainder
  identification, and the retained cross-boundary Bernoulli cancellation.

The arithmetic nonvanishing theorem is not marked proved.
