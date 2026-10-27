# Formalization coverage — Model-Theory Normalization v0.7

PASS: 44 cold-built local modules, 68 expected-outcome tasks,
1601 explicit named declarations, all axiom-audited.
Counts: {'def': 736, 'theorem': 642, 'inductive': 6, 'abbrev': 211, 'structure': 5, 'instance': 1}.
Five new generic modules add 46 theorem declarations
and 11 definitions. NormalizedExamples adds 12 concrete
theorems. Seventeen generated batches directly execute all 203 inherited profiles
through normalizedPrimeDiscover and derive all-word code certificates. Generated
facts are not independent research discoveries.

The only recorded axioms are Classical.choice, Quot.sound, propext. No custom project axioms,
sorryAx or Lean.ofReduceBool. Every accepted source hash is unchanged. Warnings
are treated as errors. All seven false/placeholder/corrupted-claim controls reject,
and the positive control accepts. Rejections are not missing-module or resource failures.

| Module | Exact checked scope |
|---|---|
| EchelonNormalize | Euclidean residue; unique representative in the pivot box; exact lattice preservation; reducedness; idempotence |
| EchelonBounds | Every pivot divides m; persistent normalized entries lie in [0,m]; insertion preserves kernel and bound |
| EchelonCanonical | Reduced basis unique for its integer lattice; normalization equality iff lattice equality |
| EchelonModularNormal | Canonical normal form equality iff equality of actual residue row submodules; storage bound |
| NormalizedDiscovery | Actual cached normalized run; exact reference and v0.6 output; returned-cache invariant; total prime-power success and original-language logical definition |
| NormalizedExamples | Negative tails, coupling, insertion-order equivalence, composite and trivial moduli, zero dimension/precision and exhausted fuel |
| NormalizedComputed00–16 | 203 direct kernel computations plus logical code consequences |

## Boundaries

The normal form is relative to fixed ambient column coordinates and a fixed modulus
for residue comparisons. It is not canonical Smith extraction or a minimal modular
generating set. The stored bound does not bound every temporary extended-gcd,
insertion, or reduction operand, nor prove total bit complexity. The numerical fuel
bound remains prime-power-specific. The Python port/parser is not verified extraction.
No minimum formula/test theorem, learned policy, or held-out performance claim.

All 479 parent Lean files remain unchanged. The current cold build
rebuilds 21 inherited dependencies and 23 new modules; it is not a fresh replay of
all historical generated suites. Upstream Mathlib is reused. Standalone Case201/202
are duplicate convenience instances and are not counted as additional discoveries.

Lean: Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
Mathlib pin: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
Review is self-review, not independent refereeing or a historical-priority verdict.
