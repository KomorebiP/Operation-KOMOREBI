# Formalization coverage — Model-Theory Normalization v0.5

PASS: **39 local modules**, including 18 inherited dependencies and 21 new modules.
**47 expected-outcome tasks** completed, including seven controls (one acceptance,
six deliberate rejections). All **2,130 named declarations** were axiom-audited.
Counts: 990 theorems, 915 definitions, 212 abbreviations, five structures, one named
instance and seven inductive declarations. Most new declarations are generated
certificate data and consequences, not independent discoveries.

Three new generic modules contribute **15 theorems, seven definitions and one
inductive data type**. CertifiedExamples adds 11 theorems. Seventeen generated
batches cover all **203 sources** (202 frozen profiles plus one new torsion stress
fixture), with four theorem applications per source.

Only Classical.choice, Quot.sound and propext occur. No custom project axiom,
sorryAx or Lean.ofReduceBool appears. The accepted sources pass warnings as errors,
and every accepted source/input hash was unchanged across the cold run.

| Module | Exact new checked scope |
|---|---|
| CertifiedMembership | Executable finite witness checking, positive/negative soundness, exact decision semantics, incompatibility of opposing valid evidence |
| CertifiedReplay | Data-driven FIFO replay, actual QueueTrace construction, complete observable span, all-word equivalence, standard logical definition, exact reference output and uniqueness |
| CertifiedOracle | Checked advice or proved enumerative fallback, arbitrary total proposer soundness, reference-result equality, universal successful return and standard defining formula |
| CertifiedExamples | Bad evidence rejection, incomplete/trailing data rejection, nonunit arithmetic, an always-wrong proposer, empty-state-coordinate boundary |
| CheckedBatch00–16 | 203 complete evidence DATA lists evaluated by ordinary kernel reduction, each with reference-result and all-word/formula theorems |

## Boundaries

The optimized Python Smith producer and exporter are not verified programs. Every
one of the 203 retained producer traces has a kernel-checked replay application;
that does not universally verify every future producer execution. The data checker
itself is a verified executable definition. The fallback's total correctness is
proved but it can enumerate exponentially many coefficients. The no-fallback replay
used by the large instances never performs that search.

The same commutative-ring membership soundness interface does not assert scalar
separators exist for every nonmember over every ring. The guarded finite-ring oracle
remains correct without that assertion. No minimum raw test-list, formula-size,
bit-complexity or relational first-order theorem is added.

Upstream runtime: Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
Mathlib source metadata pin: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Required pinned sources and
compiler hash were checked. Local modules were cold rebuilt; Mathlib was not.
All inherited proof files are preserved, but only 18 inherited modules are rebuilt.
Review is self-review, not independent refereeing or a novelty verdict.
