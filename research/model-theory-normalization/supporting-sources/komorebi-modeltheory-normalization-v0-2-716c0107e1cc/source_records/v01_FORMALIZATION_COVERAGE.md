# Formalization coverage: M1 / v0.1

Completed cold run: **6 library modules, 11 expected-outcome tasks, 119 named
library declarations audited**. Four new modules contain **44 new theorems**.
The two inherited modules are copied byte-for-byte from the v0.4 archive.

| Module | Status and exact scope |
|---|---|
| RepresentationCore | Inherited; rebuilt. Actual systems, run, behavioral quotient, exact transport, universal sufficiency. |
| FiniteCertificates | Inherited; rebuilt. Stable-horizon soundness and sufficient-test semantics. |
| ObservationalNormalization | New, 15 theorems. Total path normalizer, semantic preservation, retraction, bounded and unbounded observation-type equivalence, stable-horizon adapter, exact transport. |
| ObservationalFirstOrder | New, 8 theorems. Indexed first-order observational syntax, typed environments, surjective formula transport, actual quotient formula preservation, tuple invariance, fragment-type equivalence, distinct quantifier-rank/term-horizon measures. |
| LogicalBoundaries | New, 15 theorems. Actual failure of state-equality descent, inequality sentence failure, nonsurjective quantified witness counterexample, arbitrary delayed stream distinctions, absence of a complete finite observation-test list. |
| FiniteObservationCode | New, 6 theorems. Locally certified finite test code, its explicit quantifier-free binary formula, and exact behavioral equivalence. |

The four new modules contain 26 definitions, 2 abbreviations, 3 inductive syntax
types and 1 certificate structure in addition to their 44 theorem declarations.
Those counts describe explicit declarations, not independent discoveries.

Lean: 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Accepted library sources compile with warnings treated as errors. Every named
library declaration is printed in the axiom audit. The observed foundational
axioms are only Classical.choice, Quot.sound, propext. Negative controls for a
false statement, a placeholder, and an invalid quantifier transfer all fail;
the positive control passes.

## Not claimed

* Ordinary full quantifier-free or first-order type equivalence with state equality.
* Quantifier elimination, theory-level elimination of imaginaries, or full types.
* A Mathlib FirstOrder syntax translation. Our fragment is a precise, custom,
  Lean/Std-checked first-order syntax with only the declared observational atoms.
* That finite test bases exist for every infinite system.
* That lack of finite observation tests implies nondefinability in all larger languages.
* General ring/cost minimality or a new autonomous-discovery benchmark.
* Formal correctness of Python, its parser, or code extraction.
* Reverification of all predecessor certificates or p-adic sources.
* External referee review or literature novelty.
