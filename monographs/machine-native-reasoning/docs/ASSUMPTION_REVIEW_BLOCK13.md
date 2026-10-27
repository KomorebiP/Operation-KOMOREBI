# Core 7.4 assumption and source review

Source: `source/core_v0.2.tex:848–858`, Reviewed Core 0.2, proposition 7.4.

Primary mathematical verdict: **proved as written**, under its standard measurable probability interpretation. This is a review of the argument. Final kernel evidence is recorded separately.

| Obligation | Treatment |
|---|---|
| Actual selected false-acceptance event | The premise concerns that event, with candidate selection already incorporated. |
| Probability measure | Total mass one is explicit. |
| Event measurability | Explicit for each event used in the conditional-to-marginal bridge. |
| Pre-attempt information | Each conditioning measurable space lies below the ambient space. |
| Conditional validity | Almost-sure bound on Mathlib conditional expectation of the actual event indicator. |
| Deterministic budget | A real sequence independent of the outcome. |
| Nonnegative finite series | Nonnegativity and `Summable` are explicit. |
| Countable scope | Natural-indexed events, not a finite surrogate. |
| Stopped process | Event containment and measure monotonicity. Measurable gates give probability events. Arbitrary gates have the stated outer-measure interpretation. |
| Independence | Not assumed or needed. |
| Filtration monotonicity | Not needed for this implication once each conditional bound holds. |
| Evaluator calibration | External application obligation, not established here. |
| Adaptive random spending | Outside this deterministic-budget theorem. |
| Confidence conditional on retention | Not supplied by the stopped-event bound. |

Dependency chain: event measurability → integrable indicator → conditional-integral identity → marginal domination → countable subadditivity → summed deterministic budget. Stopping then uses event inclusion.

No source claim has been weakened to obtain a finite example. The real-series summability hypothesis spells out the finite-total premise already present in the source. No manuscript mathematical token was changed.

A separate read-only agent reconstructed the source proof and boundary cases before reviewing the new code. That offers a second reasoning pass in the same model family. It is not independent peer review or a second implementation of Lean's kernel. The code review and executable evidence must be assessed separately.
