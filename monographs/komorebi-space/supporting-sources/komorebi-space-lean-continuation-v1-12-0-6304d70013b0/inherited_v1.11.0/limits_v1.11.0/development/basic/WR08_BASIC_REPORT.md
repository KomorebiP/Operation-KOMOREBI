# WR08 basic limits and escape: development record

Status: development PASS; clean replay and independent statement audit are integration gates.

## Exact target and coverage

`RegularizationLimits.lean` defines the full real parameter path by the accepted
`RegularizedHilbertRepair.correction` at positive parameters. Every limit uses
`𝓝[>] (0 : ℝ)`, not a selected sequence. The ambient hypotheses are real complete
inner product spaces and a bounded linear operator. No closed range, injectivity,
finite dimension, separability, or positive residual-floor assumption was added.

Completed statements:

- `fitted_tendsto_projectedDatum`: fitted image tends to the range-closure projection.
- `residual_norm_tendsto_floor`: residual norm tends to the orthogonal residual floor.
- `weighted_penalty_tendsto_zero`: the weighted squared correction norm tends to zero.
- `norm_tendsto_atTop_of_not_mem_range`: unattained projected datum forces the norm to
  tend to infinity along the full positive-parameter filter.

The strong limit in the attained case belongs to the separate
`RegularizationStrongLimit.lean` task. This report does not claim that clause.

## Proof route

The exact global objective comparison from WR06 is rewritten using the accepted
orthogonal residual-square decomposition. Canceling the fixed floor gives
`objective_comparison`. For any positive tolerance, closure of the range supplies
one comparator with projected error square less than half that tolerance. That
comparator is fixed before the parameter is restricted. Its weighted penalty
then tends to zero. This proves the combined projected energy tends to zero.
Nonnegativity gives both summands' limits; continuity of square root gives fitted
image convergence; continuity of subtraction and norm gives residual convergence.

For escape, failure of convergence to infinity gives a frequently recurring finite
norm budget. The accepted arbitrary-filter WR01 realization theorem then produces
an actual preimage of the projected datum, contradicting non-membership in the
range. No subsequence extraction or monotone parameter sequence is substituted
for the original full filter.

## Preserved attempts

1. `attempt_001`: compiler rejected deprecated `dif_pos` under warning-as-error
   and an underspecified base point in `tendsto_id`. All other proof branches elaborated.
2. `attempt_002`: after naming the real zero base point and replacing `dif_pos`
   by `dite_eq_left`, the remaining elaboration required explicit simplification
   of `id` in the multiplied limit.
3. `attempt_003`: adding `id_eq` gave a clean production compile, exit 0, empty log.
4. `attempt_004`: public declarations were printed with explicit arguments and
   universes; `#print axioms` for all 10 public names gave only `propext`,
   `Classical.choice`, and `Quot.sound`.

Each attempt preserves source bytes, the exact command and environment, exit code,
elapsed time, source/log hashes, and successful object hash when applicable.
Development objects reuse a symlink overlay of the immutable accepted parent build;
that is explicitly separate from the final clean replay.

## Proofreading self-review

Proofread: the new `RegularizationLimits.lean` module and its public statements.
Routine edits: none. Mathematical-token changes during proofreading: none.
Unresolved proofreading issues: none. Validation: attempts 003 and 004 PASS.
This is an author self-review, not the independent mathematical audit.
