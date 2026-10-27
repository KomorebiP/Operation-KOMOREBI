# Observation censoring: exact scope and development record

Source: `AVOC/ObservationCensoring.lean`. Namespace: `Komorebi.AVOC.ObservationCensoring`.

The primitive model is a finite rational `CalibrationSchedule.Law (Bool × Bool)`.
The first coordinate is an underlying success/rejection; the second is whether
the outcome is retained as a checked report. Its four weights are `p*a`,
`p*(1-a)`, `(1-p)*b`, and `(1-p)*(1-b)`. All three parameters lie in `[0,1]`.
This model and its parameter bounds are mathematical assumptions, not properties
inferred from an operation log.

The source proves normalization, the underlying success marginal `p`, reported
success mass `p*a`, reported rejection mass `(1-p)*b`, and the complementary fault
mass. `retainedLaw` constructs an actual normalized law on the checked Boolean
reports when retention mass is positive. `retained_event_conditioning` proves
the conditioning identity for every Boolean event. The reported success
parameter is therefore `p*a / (p*a + (1-p)*b)`.

Equal positive retention rates recover `p`. For a nondegenerate source
`0 < p < 1`, equal rates are also necessary to recover `p` (assuming positive
retention mass). A fair source that loses every rejection and retains every
success gives conditional reported success probability one. Separate fault
logging alone does not establish the equal-retention assumption.

The deadline counterexample uses two independent fair latent bits. It always
observes the first and observes the second exactly when the first is true.
Second-report availability depends only on past history, not the current bit.
The second bit remains fair conditional on either history. Nevertheless the
experiment completes two observations with probability one half, and conditional
on completion its first observation is certainly true. Its conditional count
law cannot be binomial: zero successes have conditional mass zero, whereas
`Binomial(2,1/2)` assigns that event mass one quarter. Thus predictable selection
does not, by itself, justify conditioning a finite-deadline sample on completion.

The generic safe statement is unconditional: intersecting a bad prefix event
with the completion event cannot increase its mass. A prefix error bound `alpha`
therefore bounds the probability of producing a bad completed output. Conditional
on completion, only the weaker bound `alpha / P(completion)` follows without
further assumptions. This module proves that distinction explicitly; it does
not prove general independent latent prefixes or count laws for arbitrary
attempt traces.

Development record:

- `censor_attempt1.log`: failed the warnings-as-errors gate solely because five
  `simp` lists redundantly named `Fintype.sum_bool`. The proof goals themselves
  closed. Those redundant names were removed without disabling the linter.
- `censor_attempt2.log`: initial model and counterexamples passed.
- `censor_attempt3.log`: normalized retained law and event identity passed.
- `censor_final.log`: final module, including the necessary-and-sufficient
  interior-parameter condition, passed in 3.977 seconds. Source SHA-256:
  `93b3b9ad4c8ab53e8c90b6115f2e22014dd8812f2ed1ef9ea30efb44117734d3`.

All invocations used pinned Lean 4.34.0-rc2 and `-DwarningAsError=true` through
`tools/lean_one.py`; each invocation has a companion JSON with source/import/log
hashes. The final proof source contains no admitted obligations, project axioms,
native decision proofs, or unsafe declarations. Whole-project axiom inventory
and independent audit are release-level responsibilities outside this module.

Two requested negative tests were also added:
`tests/negative/FalseOutcomeDependentCensoring.lean` falsely asserts preservation
of the fair-source parameter under selective rejection loss;
`tests/negative/FalseCompletionConditionedBinomial.lean` falsely asserts the
completion-conditioned zero-count fiber equals the binomial fiber. Both fail
with the substantive unsolved goal `False`, after successful imports and
reduction using the proved counterexamples. Their evidence is
`censor_negative_outcome.{log,json}` and `censor_negative_completion.{log,json}`.
