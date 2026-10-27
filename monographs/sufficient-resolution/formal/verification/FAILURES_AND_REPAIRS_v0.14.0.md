# Actual development failures and repairs

Initial OperatorUncertainty drafts used the wrong side of the additive inequality
API. Replaced by explicit add_le_add with the intended unchanged summand.
ChangingDiscrepancy resolved `residual` to a topological Filter constant; qualified
the saved discrepancy residual. Removed an unused completeness hypothesis only
where the underlying theorem needs no such premise.
ChangingConsistency needed explicit unfolding of function composition in a filter
limit. The certificate proof needed explicit unfolding of Certified and elimination
of the actual Nonempty record. A deprecated sub_apply name was replaced.
Example drafts failed warning-as-error checks for an unused ext pattern, unnecessary
sequence focusing, and a tactic after a goal was already closed. All were repaired
without disabling warnings or introducing proof placeholders. Failed logs and
successful reruns are retained under development_v0.14.0.

Both final proof runs pass. The finite controls passed on their first run. No
new-block unresolved compilation, audit, replay, checker, or packaging failure is
claimed away; final actual statuses are in the current reports.
