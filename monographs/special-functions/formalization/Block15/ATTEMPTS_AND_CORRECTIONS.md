# Routes and implementation corrections

Base: f5b2651f182244afd4d979d9aed386e45c898381.
SF-B15-LADDER targets arbitrary-radius majorants. Mechanism: actual real max
recurrence, source small-disk seed and fuel induction with an explicit terminal
condition. Discriminators: radius zero and radius above the local disk.
Outcome: proved, with adequate fuel existence. The old F.2 unit-seeded ladder
route is deferred for other bounds; it was not used as a substitute for the
source's exact seed and is not exhausted.

SF-B15-TAIL targets the sharp positive outer-radius error. Mechanism: compare
each omitted exponent with beta^(2N+3), split the actual series and bound the
positive omitted sum by the full series at S. Outcome: proved, including R=0.
The Cauchy-estimate route is deferred for signed/complex coefficient regimes;
its usual geometric denominator would give a weaker certificate here.

SF-B15-RATIONAL targets exact endpoint semantics. Mechanism: fuel cast identity,
an independent ordinary rational coefficient recurrence, canonical coefficient
uniqueness and finite-sum/max cast identities. Outcome: proved for the Lean
rational model and exact interval endpoints. Python program refinement remains
open, with factorial normalization and guarded loop behavior as next leaves.

Development diagnostics were API/implementation corrections: addition bound
orientation needed explicit add_le_add; deprecated if_pos/if_neg names were
replaced; reflexive real-radius comparison was made explicit; rational casts
needed normalization on both sides; nested coefficient recursion used its
equation theorem; rational type methods needed explicit namespace arguments;
an unnecessary tactic-sequence focus was removed under strict linters. None
refuted the registered mathematical target. The worked theorem name was
calibrated to last index 30, which retains 31 terms, rather than calling it
a thirty-term truncation. The final production compiles with warnings as errors.

Rejection fixtures attempt equal outer radii, insufficient fuel, a shifted
inclusive-index exponent and a placeholder. These verify theorem interfaces;
a type rejection alone is not a new mathematical counterexample. The positive
fixture checks zero input, arbitrary-radius existence, exact rational casts,
the worked complex error and actual rational endpoint containment.

No numerical fit, random sampling, novelty claim, delegated job or delayed
mathematical run supports the result. Development diagnostics are labeled
separately from accepted proof evidence; any failed formal replay is preserved
separately in the I/O manifest. Manuscript and Python sources were not edited.
