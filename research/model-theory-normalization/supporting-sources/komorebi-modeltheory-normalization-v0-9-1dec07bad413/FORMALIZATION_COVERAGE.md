# Formalization coverage — Model-Theory Normalization v0.9

PASS: 53 cold-built local modules: 31 inherited
and 22 new. Four new generic modules contain
38 theorem declarations, 19 definitions and one
abbreviation. One example module and seventeen generated modules complete the new
scope. All 203 generated statements compute both the result and its exact arithmetic
counter in the Lean kernel.

79 expected-outcome tasks passed: 53 module builds, 18 axiom groups,
one positive control and seven deliberate rejection controls. All
1701 explicit named declarations were axiom-audited:
{'def': 762, 'theorem': 715, 'inductive': 6, 'abbrev': 212, 'structure': 5, 'instance': 1}.

Only Classical.choice, Quot.sound, propext occur. No custom project axiom, sorryAx or
Lean.ofReduceBool. Library warnings are errors. Accepted input and compiled-output
hashes were unchanged across the audit. The negative controls fail for their proof
claims, not missing imports or resource caps.

| Module | Exact formal scope |
|---|---|
| CostedPrimitives | Recursive metered Euclid/gcd, signed wrappers, dot and row/test evaluators; value projection and exact arithmetic counts |
| CostedLattice | Metered triangular membership, residue, insertion and normalization; erased values equal originals; exact count identities and magnitude-linked update bound |
| CostedDiscovery | Actual costed FIFO computation; exact value refinement at every fuel; total prime-power discovery and inherited first-order definition |
| CostedBounds | Per-update and whole-run declared arithmetic-unit bounds; explicit polynomial in fuel, dimension and modulus-bit budget |
| CostedExamples | Zero/negative/modular boundaries, failed membership, initial normalization, exact insertion and noncommuting word examples |
| CostedComputed00--16 | All 203 exact result/count computations and all-word code consequences |

## What is not proved

The count is for the declared high-level arithmetic model, not CPU, elapsed-time,
allocation, bit operations, source parsing, output serialization or theorem-kernel
work. The eager-array sharing interpretation is not proved to be the actual cost
of Lean function-valued vectors or its native runtime. Integer primitives are not
implemented as a verified bit-cost backend. The Python port and exporter are not
verified extraction. The raw returned tests need not be minimal. No held-out
mathematical discovery, universal relational reasoning or historical novelty is claimed.

All 530 inherited Lean library source files under formalization/ are preserved unchanged. Only the 31
imported inherited modules are rebuilt here; all historical generated suites and
upstream Mathlib are not rebuilt. The original complete predecessor is frozen in
history/; five baseline Python modules are copied unchanged for independent checks.

Lean: Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
Review: authoring-assistant self-review, not an independent referee.
