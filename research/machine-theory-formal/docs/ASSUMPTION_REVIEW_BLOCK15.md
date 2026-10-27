# Core 8.2 assumption and source review

Source: `source/core_v0.2.tex:888–898`, with the finite institutional-state context at line 886.

The source argument is sound for deterministic successors defined on enabled actions. Its uniqueness statement is interpreted on that legal domain. Final executable evidence remains separate from this mathematical review.

| Obligation | Treatment |
|---|---|
| Protected labels | Actual functions on concrete and quotient states. |
| Enabled-action sets | Retained as an explicit fibre and factorization obligation. |
| Determinism | An enabled state/action pair has one successor. |
| Partial legal domain | Canonical `Option` representation, with `none` exactly for disabled actions. |
| Source translation | Separately supplied enabled sets and dependent legal successors translate exactly to the partial-system representation. |
| Surjectivity of π | Explicit; supplies representatives and uniqueness at every quotient state. |
| Fibre labels | Equal fibres have equal labels. |
| Fibre availability | Equal fibres enable exactly the same actions. |
| Fibre successors | Projected successors agree whenever the action is enabled. |
| Quotient construction | Defined from representatives and proved to factor the actual data. |
| Uniqueness | Actual partial quotient data, not arbitrary total values at disabled actions. |
| Finiteness | Finite states and finite action alphabet retained in source-facing statements. |
| Empty types | No unnecessary nonempty-state assumption. |
| Words | Arbitrary finite action lists, executed left to right. |
| Labels along execution | Initial label and every intermediate/final label are retained. |
| Legality | Preserved and reflected along related initial states. |
| External authority | Not derived from encoded permissions. |

The generic proof requires no finiteness because representative factorization and finite-word induction do not use a cardinal bound. The source-facing specialization retains finiteness explicitly. No probabilistic, nondeterministic or partially observed operational model is silently substituted.

A total function can assign different values to a disabled action without changing legal behaviour. Such values are not covered by the source's uniqueness statement. Canonical absence removes this irrelevant choice while the explicit source translation proves that all supplied legal transitions are retained.

The independent agent review is an additional reasoning pass within the same model family. It is not independent peer review or a second implementation of Lean's kernel. The current release requires its own completed cold gates and source bindings.
