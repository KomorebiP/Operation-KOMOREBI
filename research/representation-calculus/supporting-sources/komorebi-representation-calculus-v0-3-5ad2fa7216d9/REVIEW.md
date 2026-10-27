# Adversarial proof review — self-review

## Primary verdict

**Proved as written** for the generic matrix adapter, actual-image factorization,
state-space minimality injection, generated instance theorems, and the specialized
large cardinality/two-coordinate endpoints. The universal numerical free-linear
minimum for arbitrary matrix certificates is explicitly outside that verdict.

| Obligation | Resolution |
|---|---|
| Words and matrix order | wordMatrix cons order agrees with left-to-right source run; row right action prepends the digit |
| Source object | Literal expected matrices are emitted; independently reparsed; no finite state-space surrogate |
| Forward semantic inclusion | PA=CP and O=DP imply every finite word's outputs agree |
| Converse inclusion | Each encoded row is a combination of verified actual word observations |
| Exact target | Actual image subtype is closed and encoding onto it is surjective; ambient array need not be reachable |
| Torsion | Smith image uses genuine scalar multiples, no inverse of a nonunit |
| Empty tests | Fin 0 handled; 17 zero-coordinate instances compile with singleton image |
| Unrestricted competitors | Generic state-space lower bound uses all-word correctness, not assumed local transition correspondence |
| Large sharp bound | Compact bijection to Fin(2^30), not enumeration; zero/one residue coordinates pack injectively into Fin65536 |
| No circular provenance | Shared row base/step proofs precede their uses; W combinations are checked only after true row semantics |
| Wrong source | Rebound-hash control fails the actual matrix equations |
| Kernel trust | All positive declarations audited; no custom axioms, sorryAx or native reduction axiom |
| Code verification | Parser/exporter/discovery are not certified executable programs; this remains a boundary |
| Novelty and benchmarks | No originality or speedup claims; synthetic regression fixtures only |

The formal kernel check is distinct from this review of what the statements mean.
This review was performed in the same interaction, not by an independent agent.
