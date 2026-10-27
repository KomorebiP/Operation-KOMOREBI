# Formalization coverage — Representation Calculus v0.4

## Completed execution

PASS: a new cold build of 235 local modules, 259 expected-outcome main tasks,
and two supplementary tasks (attributed-declaration axiom audit and fresh exporter
instance). The main audit covers 6,192 named library declarations. The separate
inventory pass adds the three same-line `@[simp]` lemmas, for **6,195 explicit named
library declarations**: 3,833 theorems, 2,147 definitions, 208 abbreviations,
five structures, and two named instances. Generated internal auxiliaries are
compiled but not separately counted. Most declarations are inherited/generated
certificate facts, not independent discoveries.

Only `Classical.choice`, `Quot.sound`, and `propext` occur in the dependency audit.
There are no additional project axioms, `sorryAx`, or `Lean.ofReduceBool`.
Both positive controls were accepted. The nine expected rejection controls were
rejected, including bad encoding/Smith/provenance, bad nonzero-factor/prime claims,
nonlinear-as-linear encoding, a false proposition, and a sorry placeholder.
Accepted source hashes were unchanged across the full run.

Lean 4.34.0-rc2: `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
The cold audit rebuilds local modules using the pinned upstream dependency cache;
it is not a rebuild of the entire Mathlib library.

## New checked scope

| Module | Exact checked content |
|---|---|
| MatrixLinearBridge | Predecessor matrix sums agree with Mathlib linear maps; any sufficient encoder must preserve certificate-image distinctions; the image of a sufficient linear encoder surjects linearly onto the actual principal factors |
| FinRingCompatibility | Std and Mathlib modular semiring structures agree on their real operation data, allowing uniform symbolic transport without recomputing concrete matrices |
| MatrixPrimeMinimality | Generic prime-power lower bound and sharp budget iff; arbitrary deterministic target operations/observations are permitted but initial encoding is linear; modulus and Fin wrappers retain the original source semantics |
| MinimumBatch00–12 | All 202 frozen certificates have a kernel-checked nonzero-factor premise and a universal minimum-coordinate budget theorem |
| CertifiedMinima | Import-only aggregate of those 202 endpoints |
| TorsionEncodingBoundary | Two order-two factors modulo 16 need two linear coordinates, but one nonlinear residue encoding preserves every future observation; the packing is not additive |
| LargeLinearMinimum | The inherited large synthetic source obtains the same two-coordinate minimum from the generic algebraic theorem |
| KomorebiPadic/FiniteGenerators, PrincipalIdealGenerators, PrimeIdealGenerators | Three byte-preserved prior project modules are rebuilt, supplying integer-lattice and nonzero-principal-factor generator bounds |

The 213 inherited Lean files have only module/public-import header migration in
the current tree; bodies and literal data are unchanged. Original bytes remain in
the frozen v0.3 archive. `PARENT_BODY_REPLAY.json` checks all 213 mathematical
bodies, and the finite audit checks all 202 source/certificate pairs.

`examples/FreshMinimum.lean` is freshly emitted by the new exporter and compiled
separately. Its explicit tables/matrices and minimum theorem are kernel-checked.
Its names are not counted again in the library declaration total above.

## Boundaries

This closes the missing generic numerical free-linear minimum theorem for accepted
prime-power matrix certificates. It is not an arbitrary-program space bound.
The all-source-state contract and linear initial encoding are load-bearing.
Single-seed problems and nonlinear initial encodings have different minima.

Python discovery, its stopping loop, its parser, the Smith engine and exporter
remain unverified executable programs. Lean checks literal generated source,
not an informal human problem that might have been encoded incorrectly. No
trained proposer, held-out scientific discovery, cross-domain performance study,
independent referee verification, or historical priority is claimed.
