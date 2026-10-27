# Self-review and dependency boundary — v0.10

Primary verdict: **proved as written for the scalar backend and declared cost
contracts; incomplete for the original end-to-end discovery bit-runtime target.**

The reviewed dependency chain is Boolean truth tables -> ripple identities ->
long multiplication/division invariants -> signed adjustment -> value erasure ->
width-sensitive recurrence bounds. Native ring identities and division uniqueness
are explicit standard inputs, not desired implementation properties assumed as
hypotheses.

| Obligation | Verdict |
|---|---|
| Carry/borrow exactness and zero-length boundary | Passed |
| Equal-width subtraction premise | Explicit, supplied by padding |
| Positive divisor and remainder range | Passed; raw zero-divisor theorem not claimed |
| Negative dividend Euclidean adjustment | Passed |
| Leading zeros and negative zero | Passed |
| Modular product wider than operands | Passed; 3B padded-width bound used |
| Metered value computed recursively, matching unmetered bit routine | Passed |
| Cost recurrences and quadratic budgets | Passed in stated gate/cell model |
| Explicit unsigned trace values/cost | Passed under validity/width/length premises |
| Full solver port matches independent frozen results | Finite evidence, 203 fixtures |
| Full discovery lowering to persistent binary states | Not addressed by a universal Lean proof |
| Encoding/decoding cost, queue/index/allocation/sharing refinement | Open |
| Native runtime or bit-machine polynomial cost | Open |
| Independent researcher review / historical novelty | Not performed |

A source specification and its compiled certificate cannot prove their own faithful
encoding of an informal problem. The original finite-linear observational contract
is unchanged. No unrestricted model-theoretic preservation or universal algorithm
lower bound is inferred from this arithmetic layer.
