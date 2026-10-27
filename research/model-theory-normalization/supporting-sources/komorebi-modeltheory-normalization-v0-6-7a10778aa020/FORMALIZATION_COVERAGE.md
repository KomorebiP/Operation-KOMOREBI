# Formalization coverage — Model-Theory Normalization v0.6

PASS: **39 local modules**, 17 inherited dependencies and 22 new
modules, including 17 batches executing all 203 profiles. The four new generic
modules contain **37 theorem declarations,
17 definitions, and one recursive basis type**.
EchelonExamples adds 13 concrete theorems. Each generated profile has one actual
kernel computation and its all-word logical code consequence.

All **1536 explicit named declarations** were axiom-audited:
{'def': 716, 'theorem': 597, 'inductive': 6, 'abbrev': 211, 'structure': 5, 'instance': 1}. Counts include generated data, not independent discoveries.
The audit completed 48 logical stages using
55 actual Lean process invocations: 39 cold module builds, eight bounded
axiom groups and eight controls. All seven intended rejections occurred for their
proof claims, not missing imports or resource limits. The positive control accepted.
Only Classical.choice, Quot.sound, propext occur. No custom project axiom, sorryAx or
Lean.ofReduceBool. Accepted source hashes were unchanged. Local sources are
checked with warnings as errors. Upstream Mathlib was reused, not rebuilt.

| Module | Exact formal content |
|---|---|
| EchelonCore | Actual positive-pivot integer basis, injective synthesis, terminating executable triangular membership and reconstruction |
| EchelonInsert | Actual gcd/Bezout update, structural insertion, both integer-span directions, exact submodule join |
| EchelonModular | Kernel m Z^d, integer lift/reduction, exact preimage invariant for every positive modulus, executable membership soundness/completeness |
| EchelonDiscovery | Cached basis through FIFO updates, equality with every correct oracle at every fuel budget, total prime-power discovery, actual standard first-order formula |
| EchelonExamples | Nonunits, composite modulus, negative integer insertion, coupled congruence, degenerate dimensions/precisions and insufficient fuel |
| EchelonComputed00–16 | All 203 actual computations by decide +kernel, not supplied trace replay; corresponding all-word finite code certificates |

## Precise boundaries

The algorithm is integer echelon, not canonical Smith/Hermite reduction. It stores
exactly d integer rows, not necessarily a minimal MODULAR generating family. There
is no nonunit modular inversion, exhaustive coefficient search or untrusted adviser
in fastPrimeDiscover. Its prime-power totality uses the inherited enough-fuel bound.
The positive-modulus membership/update theorem is broader than that assembled bound.

The Python port/exporter is not verified code extraction. No formal bit-complexity,
coefficient-growth bound, minimum test-list/formula theorem, relational discovery,
learned policy or held-out benchmark is claimed. The new numerical fixed-instance
outputs equal old lists, not newly asserted minimum linear bases.

All 254 parent Lean files are byte-preserved. Only 17 inherited local
dependencies were freshly rebuilt. Standalone EchelonCases files duplicate the case
content exercised in the batches; they are not counted as additional research or
claimed to have a second complete cold build. Case201 and Case202 also had separate
development checks. Fresh extraction scope belongs in the external replay report.

Lean: Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
Mathlib pin: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
Proof interpretation is self-review, not independent refereeing or priority review.
