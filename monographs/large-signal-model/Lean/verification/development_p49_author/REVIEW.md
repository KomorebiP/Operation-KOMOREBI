# P49 source-to-target review

Frozen source: `KomorebiLSM/CertificateLearning.lean`, SHA256 `b24586e77d2b3589d2f67eb2611435e0cda1b8b9eedc60b755cc8c6f99f2ea0c`.
Original target: `source/FOUNDATIONS_1.0.0.md` lines 2172–2183, Proposition 49.

| Source clause | Checked target |
| --- | --- |
| Observable identification assumptions of P37 | `observableModel`, `observable_word_probability`, `observable_minimal` use the actual invertible core/rank-bound table realization. |
| Checked finite witness gives internal validity at every horizon | `Witness` contains literal nonnegative coefficient matrices, intertwining equations, exact per-action mass law, initial prior and initial lift. `certified_all_words`, `modelLaw_prior`, `observedLaw_prior` derive the conclusions. |
| Whole uncertainty set and initial states share the domain | `robust_vertex_witness` uses P40 convex-hull extension and explicit initial coverage; `witness_exists_iff` constructs actual matrix columns. Both confidence theorems demand these actual witnesses, not a validity predicate equal to their conclusions. |
| Supplied justified confidence event | `conditional_learning`, `conditional_selected_learning`, `conditional_observable_learning` assume one explicit measurable event and its actual measure lower bound. They do not define an arbitrary possibly nonmeasurable validity event or invent concentration. |
| Fitted and true common-policy law TV budget | `certified_policy_bounds` proves the displayed clipped bound for actual joint action/observation records and observation-only records under every common randomized history policy and every horizon. |
| Data-selected finite domain | `conditional_selected_learning` permits dependent finite generator index `K ω` and synthesis map `V ω`, after seeing data. |
| Conditioning P44 | `certified_conditioning` and `certified_observation_conditioning` use actual laws and retain both positive event-mass hypotheses. |
| Exact atlas transport | `atlasWitness`, `atlas_normalized`, `atlas_surjective`, `atlas_word_probability` use V'=TV, conjugated B, transported mass, identical coefficient matrices and prior. |
| Complete signed packet synthesis | `full_packet_prediction` proves actual full-law prediction identity. `positive_packet_interpretation` and `positive_packet_state` separately require cone positivity; individual normalized packets require positive mass. |

The generic finiteCone statements use surjective V, the full-row-rank premise already present in P39. `witness_surjective_of_reachable` and `observable_witness_surjective` additionally derive this premise for any actual true observable-model witness using P37 reachability. Coverage and error budgets remain the explicit conditional hypotheses of P49, rather than statistical conclusions manufactured by this file.

Verification: clean pinned Lean compile with warnings as errors; all 34 explicitly named declarations audited, only propext/Classical.choice/Quot.sound; entire imported module replayed by pinned upstream LeanChecker. Both dedicated controls reject with an actual False goal (mass alone does not imply nonnegativity; signed synthesis does not make every packet a probability).

No sorry, added axiom, unsafe declaration, native_decide, or unproved stochastic-validity assertion is used.
