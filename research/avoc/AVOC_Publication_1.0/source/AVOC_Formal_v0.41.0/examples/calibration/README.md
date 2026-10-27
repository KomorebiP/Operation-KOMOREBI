# Finite-checkpoint operation calibration

The calibration command constructs a conservative exact-rational probability
interval from a protected binary operation log. It uses the same uniform-grid
cell rule as `AVOC/FiniteCalibration.lean`. The parser and operation-log adapter
are Python. Their agreement with the Lean function is checked on finite examples,
not established by a universal implementation-refinement theorem.

## Statistical contract

Before observing the data, fix the authority record, exact identity strata,
uniform rational grid, sample-size checkpoints, and their error allocations.
The sum of all allocations, across every identity and checkpoint, must not exceed
the declared global alpha. Repeatedly inspecting the same fixed-checkpoint result
does not allocate a new statistical event. Choosing a new schedule after looking
at outcomes falls outside the contract even if the parser accepts the new file.
The parser cannot determine when an authority was actually registered.

Within each identity, assume the counted checked outcomes are IID Bernoulli with
one fixed probability. This is a supplied statistical model. Exact identity
matching alone does not establish stationarity, independence, exchangeability,
or empirical calibration. Operational changes require a different stratum and
a prospectively allocated error budget.

Infrastructure faults and unfinished intents are excluded. This exclusion is
statistically justified only under an explicit noninformative observation or
selection assumption for the target probability. If timeouts depend on the
latent outcome, the retained sample can be biased. Without that assumption, the
interval applies at most to the checked-outcome distribution specified by the
model, not automatically to success of every attempted external operation.
The log must be complete and preserve operation order. These are trusted input
boundaries, not consequences of parsing or of an evidence identifier.

For sample size `n`, success count `k`, and allocated error `alpha`, retain a
uniform grid cell `[l,u]` precisely when

    choose(n,k) * u^k * (1-l)^(n-k) > alpha / (n+1).

Return the hull of retained cells. Return `[0,1]` for no data or an empty retained
set. All arithmetic uses integers and `fractions.Fraction`. For every parameter
inside a cell its binomial count mass is at most the cell envelope. Consequently
an excluded parameter has observed count mass at most `alpha/(n+1)`. The universal
probability argument and its assumptions belong to the Lean proof, rather than
to the finite regression described below.

## Input schema

`n100_k80.json` is a complete request. It contains:

- `schema`: exactly `avoc-calibration-v1`.
- `authority`: authority identifier, global alpha, the fixed uniform grid, and
  exact identity strata with increasing `{n, alpha}` checkpoint schedules.
- `selected_identity`: the exact nine-field F5 quote identity used by v0.38.
- `checkpoint`: one of that identity's predeclared sample sizes.
- `events`: immutable operation summaries, each containing exactly
  `operation_id`, `identity`, `status`, and `evidence_id`.

The only counted statuses are `checked_success` and `checked_rejection`.
`infrastructure_fault` and `intent` are excluded. A repeated identical operation
record is idempotent. Reusing an operation identifier for any different record
is rejected, including changing a fault into a checked rejection. The sample
is the first `n` unique checked records in supplied log order for the selected
identity. Other identity strata cannot contribute outcomes.

This interface consumes immutable summaries, not a lifecycle-event journal.
An `intent` record identifies a still unresolved operation in the snapshot.
A durable lifecycle system must first reconcile its committed result and
produce a new authenticated summary snapshot. Appending a conflicting terminal
record to the old snapshot is deliberately rejected.

Numbers are JSON integers or reduced nonintegral rational strings such as
`"1/20"`. Integral fractions use integers, so `"1/1"` is rejected. Floats,
booleans used as integers, nonfinite values, duplicate JSON keys, unreduced
fractions, unknown fields, unknown statuses, and overallocated schedules are
rejected. Resource caps are 2,000 observations per checkpoint, 1,000 grid cells,
100 identities, 100 checkpoints per identity, and 20,000 supplied records.
Exceeding a cap is a rejection, never a silently truncated calibration.

The authority and exact identity are retained in the result. SHA-256 values are
only provenance fingerprints. Equality of protected identity records uses the
decoded fields, with no assumption of hash injectivity. The parser performs no
signature verification and cannot authenticate a claimed checked result.

## Run

From the project root:

```bash
python3 tools/calibrate_quote.py examples/calibration/n100_k80.json
python3 checks/test_calibration.py
python3 checks/test_calibration.py --lean
```

After rebuilding the inherited robust-quote Lean endpoint, a new planning
request can be evaluated using the actual v0.38 functions:

```bash
python3 tools/calibrate_quote.py examples/calibration/n100_k80.json \
  --plan examples/robust_quote/uncertain_plan.json
```

Set `AVOC_LEAN_KIT` to the pinned runtime location before using `--plan`.
Missing runtime objects or a failed Lean invocation produce an explicit error.
The independent oracle never calls the Lean Bellman evaluator.
With `--plan`, the command first invokes the actual Lean calibration function,
checks its exact endpoints against the Python implementation, and uses the Lean
endpoints in the subsequent actual Lean planning call. Without `--plan`, the
command computes only the Python interval and does not claim Lean execution.
The planning call uses `calibrated-quote-plan-f5-v1`, which also runs the proved
`CalibrationBridge.competitorDominanceCheck`. Read the returned
`competitor_dominance` list for this certificate. The nested `lean_plan` preserves
the inherited v0.38 response, whose older dominance annotation also compares
an action against itself and therefore cannot certify a positive-radius action.

Replanning is blocked if any unresolved intent appears in the supplied
protected log. A successful call creates a separate planning value with the
selected probability interval replaced by the new interval. It preserves the
old plan, selected deterministic quote fields, state, and unselected quote.
It does not write to an existing intent or acknowledge an operation. The prior
interval is not intersected with the new interval: doing so would require its
own coverage premise and joint error accounting. The output retains both the
old interval and the new calibration provenance when `--plan` is used.

Replanning changes the fixed quote model for a new episode. Repeated adaptation
within an ongoing episode is not justified by the inherited fixed-model
whole-policy regret theorem without an additional model-change argument.

## Bounded executable evidence

`checks/test_calibration.py` evaluates all `n=0,...,12`, every count, parameters
`p=j/40` for `j=0,...,40`, and three alpha levels. It independently builds count
probabilities by repeated Bernoulli convolution, checks normalization, verifies
the excluded-mass implication, and sums the exact miss probability. A separate
oracle enumerates all binary sequences for `n<=8` at five parameter values.
Neither oracle calls the production binomial-coefficient expression.

The examples also include `n=100,k=80` and `n=500,k=400`, each using alpha
`1/100` and 100 cells. The generated bands are respectively `[31/50,93/100]`
and `[7/10,22/25]`. A separately fixed 1,000-cell authority for `n=500,k=400`
produces `[361/500,433/500]`. In the inherited uncertain-plan example, this
changes the robust recommendation from cold generation to warm inspection.
The finer-grid authority is a separate prospective scenario, not a retroactive
change to an already registered authority. These are synthetic operation logs, not measurements of
production success probabilities. The bounded checks establish neither a
universal probability theorem nor empirical adequacy of the supplied model.
