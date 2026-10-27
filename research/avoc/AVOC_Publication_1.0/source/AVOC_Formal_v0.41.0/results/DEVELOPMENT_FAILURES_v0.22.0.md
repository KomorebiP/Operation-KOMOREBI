# AVOC v0.22.0 — failures and repairs

## Environment/tool failures

- One container response failed with a transport error. Its attempted output was
  not used; a smaller read succeeded.
- Interactive streaming execution was unavailable. Runtime assembly/extraction
  was executed synchronously instead. A command initially referenced assemble.py
  before extraction, then the starter was explicitly extracted and run.
- The first final clean-build slice exceeded the host execution limit. After
  verifying that no old Lean child remained, unfinished targets were resumed.
- An early negative-test batch was started before the clean aggregate/import
  graph was ready and was interrupted. Some cases therefore failed at missing
  imports. They were NOT counted as substantive negative evidence. The entire
  50-file suite was rerun after all 119 local targets compiled. The incomplete
  early batch log is retained separately.

## Lean development repairs

- Unfolding the Guarded system inside value terms too early prevented terminal
  lemmas from matching. The proofs now use explicit continuation expressions.
- Warnings-as-errors caught redundant tactics and unused simplification arguments.
- A nonexistent namespaced Finset.sum_div lemma was replaced by finite-sum
  multiplication with an inverse. Deprecated dif_pos was replaced by dite_eq_left.
- Rewriting rational predicates directly inside decide introduced dependent
  Decidable-instance mismatches. The proofs now transport the corresponding
  Boolean truth propositions before rewriting.
- Initial ledger arithmetic left record projections unreduced. An explicit
  remaining-credit/count proposition allows exact natural-number arithmetic.
- Record-update formatting and a Boolean lemma-name mismatch were repaired.
- Proofs around monadic fault-update parsing were unnecessarily dependent. A
  separate typed updatedJob and explicit match/if updater made the interface
  theorem direct.
- Concrete example scripts initially unfolded configuration records before named
  mean identities could match. Exact finite rational normalization replaced those
  fragile rewrite orders.

No mathematical release claim had to be weakened after a counterexample in this
block. The improving-service counterexample is intentionally retained to refute
an OVERGENERALIZED threshold rule; the theorem itself explicitly requires
NoRevival, which is proved for the declared persistent-type specialization.

## Scope not silently upgraded

The advisor is read-only. It has not been represented as a new automatic keyed
retry coordinator, a physical fault detector, an empirical calibration result, or
a production LLM research system. Nominal per-attempt cost is not total runtime
cost. Inherited atomic recovery and proof-admission implementations are unchanged.
