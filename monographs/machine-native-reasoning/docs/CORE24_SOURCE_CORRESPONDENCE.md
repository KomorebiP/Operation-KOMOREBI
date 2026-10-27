# Core 2.4 source correspondence

| Source object or obligation | Actual formal object or endpoint |
|---|---|
| Fixed candidate family T and distinguished reference A | `T : Theta -> A -> V ->_l[K] V`, explicit `theta0`; `source_core24_reference` also accepts R with `T theta0 = R` |
| Words executing the first listed action first | `wordMap`, `wordMap_eq_run`, `wordMap_append` |
| Propagated span E | `generators`, `discrepancy`, `generator_mem` |
| All initial vectors, every fixed candidate, every finite word | `ObservableAgreement`, checked again as pointwise equations in the API |
| E lies in the protected readout kernel | `agreement_iff_invisible` |
| Reference invariance and invariance under every candidate | `reference_invariant`, `candidate_invariant` |
| Actual quotient V/E and shared updates | `quotientUpdate`, `quotientUpdate_candidate` |
| Descended protected readout | `quotientReadout`, `quotientReadout_mk` |
| Existence of a complete common model | `CommonModel`, `canonicalModel`, `agreement_iff_commonModel` |
| Necessary direction for arbitrary function updates/readout | `agreement_of_function_factor` |
| Candidate switching between operations | `switchedMap`, `switched_quotient`, `switching_output` |
| Finite span iteration terminates | `seed`, `closureStep`, `stage`, `bounded_plateau`, `stage_finrank_eq` |
| Complete source endpoint | `source_core24`, `source_core24_reference` |

The canonical source, source PDF and 27-entry source index are unchanged. The
existing result number, title, lines and printed page are checked against that
index by the complete verifier. Source maps only record an accepted formal
status when the current complete gates and comparison pass. The program's
English prose is not certified merely because a declaration has a similar name.

The source speaks about a common linear quotient, not necessarily a minimal
predictor. The formalization retains that distinction. Choosing another actual
reference yields the same discrepancy submodule, but arbitrarily replacing the
reference by a system outside the family can invalidate the equivalence.

Review level: source-to-formal reasoning review within this development, plus
source-facing compiler checks and explicit counterexamples. No external
independent review or historical-priority judgment is asserted.
