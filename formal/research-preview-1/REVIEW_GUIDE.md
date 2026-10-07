# Review path

Begin with C01, C03, C04, and C06 in `CLAIMS.md`. These carry the public theorem.
The minimality contract fixes the ring and alphabet and compares all words, not only
canonical numeral encodings. The coefficient order is least-significant first.

Read `CanonicalMaskAutomaton.lean` for construction and all-coefficient output,
`CartierMaskTransition.lean` for the actual formal-series transition,
`ResidualBehavior.lean` for the intrinsic prefix residuals, and
`CanonicalLinearRealization.lean` plus `MinimalMaskRealization.lean` for the
cross-realization comparison. The unchanged intermediate modules supply the reduction
chain; their block chronology is not the required reader order.

Counterexamples in `ResidualMinimalityExamples.lean` distinguish linear minimum from
DFA minimum and all-word equality from agreement on canonical encodings. The actual
source hypotheses, not an informal headline, determine what is proved.

For an objection, report the claim ID, declaration, exact input or counterexample,
expected conclusion, observed behavior, and toolchain where applicable. A finite
implementation bug and a formal theorem error are different incidents. Preserve the
failing release and publish a correction with an explicit change in status.

The default review status is author/AI self-review with kernel checking and orthogonal
finite checks. Independent review is invited, not falsely implied or required as
permission to publish.

Read [ATTRIBUTION.md](ATTRIBUTION.md) for the source/context distinction and [FUTURE_RESEARCH.md](FUTURE_RESEARCH.md) for proposals explicitly outside the current theorem.
