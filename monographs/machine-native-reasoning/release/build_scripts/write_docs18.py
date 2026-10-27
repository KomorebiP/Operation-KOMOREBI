from pathlib import Path
import json, hashlib
R=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25')
(R/'README.md').write_text('''# Machine-Native Reasoning — positive packet mixtures

Formal companion 0.18.0. Author: Komorebi P.

This cumulative project targets Core 2.5 of the unchanged Reviewed Core 0.2. The
previous accepted correspondence is 25/27. The configured map has 26 explicit
source targets, including both sectors of Core 2.5. This preparation record is not
an admission receipt: acceptance requires the completed current-source and
separately extracted-source gates and their comparison. See `release/` for any
subsequently generated acceptance record, report and exact continuation ledger.

## Mathematical entry points

* `Komorebi.MachineTheory.PositivePackets.source_core25`: finite positive-cone
  mixture, strict mass, zero-packet equivalence and positive-only normalization.
* `Komorebi.MachineTheory.PositivePackets.Coordinate.source_core25_coordinate`:
  positive complete idempotents on the coordinate cone are disjoint selectors.
* `Komorebi.MachineTheory.PositivePackets.Coordinate.classification_iff`: the
  converse characterizes exactly these coordinate-selector families.
* `Komorebi.MachineTheory.PositivePackets.Transport.source_coordinate_change`:
  simultaneous transport of cone, mass and operators through a linear equivalence.

The general mixture theorem requires neither idempotence nor finite dimension.
The classification has finite coordinates and assumes the standard nonnegative
cone. Signed coordinates may represent valid probabilities in a transported cone.
The positive-index type prevents a zero-weight packet from becoming a unit-mass
state through Lean's totalized inverse. Empty indices and zero-dimensional
coordinate spaces are not silently excluded.

## Reproduction

Use the stored portable Lean 4.34.0-rc2 runtime and pinned nine repositories.
Do not substitute an online newest toolchain. Set the runtime location and run:

```sh
export KOMOREBI_LEAN_RUNTIME=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python scripts/supervise.py --runtime "$KOMOREBI_LEAN_RUNTIME" --out evidence/local18 --whole-timeout 1800
```

The output directory must be new. Each Lean command has a 45-second wall limit,
one worker, a 4096 MiB internal limit, and warnings treated as errors. The verifier
cold-builds every production module, checks the actual source-facing interfaces,
audits transitive axioms, replays substantive modules through Lean's own kernel,
checks the complete rejection manifest, and hashes actually imported dependencies.
It does not rebuild Mathlib or independently authenticate the origin of its cache.

`python scripts/check_positive_packets.py --out /tmp/positive-packets.json`
runs the separate exact rational regression. Finite checks do not replace proofs.
Runtime recovery tools and installation receipts are supplied without binaries.

## Preservation and delivery

All 71 predecessor substantive modules and five original source-book files are
pinned in `PREDECESSOR.json`. The complete prior archive was intact and verified.
Earlier Core 8.3 historical recovery gaps remain documented in predecessor history;
they are not a new loss of the current formal source. The original monograph is
not rebuilt in this proof task. Core 3.2 remains the next selected target.

Source code and machine-readable original material retain MIT licensing, and
original prose retains CC BY 4.0, with upstream terms and exceptions preserved.
No runtime or standalone font binaries are included. See the retained notices.
''',encoding='utf-8')
(R/'PROGRESS_LEDGER.md').write_text('''# Core 2.5 preparation ledger — 0.18.0

Date: 23 October 2026. Stage: source preparation and development checks.
This file is a proof-gate input and will not be silently edited after acceptance.
The later `release/ACCEPTED_PROGRESS_LEDGER.md` and actual receipts, if present,
record the final verdict. An endpoint label in the theorem map is not its receipt.

## Previous accepted state

Core 2.4 companion 0.17.1: 25/27 mapped source results. The complete 62,071,022-byte
archive was authenticated and extracted. All 2,176 manifest files passed. The
71 substantive Lean modules and five original source-book files remain unchanged.

## Current mathematical work

Four production modules add the general convex-cone mixture theorem, the complete
coordinate-idempotent classification, linear-equivalence transport, and explicit
boundary examples. The raw source-facing API retains all hypotheses. There are
102 authored declarations, of which 73 are supporting theorem declarations. This
closes at most one additional source result after acceptance, not 73 discoveries.

The mixture omits zero packets by a positive-index subtype and proves the omitted
packets vanish. The coordinate sector constructs coordinate ownership and derives
disjointness rather than assuming diagonal matrices or orthogonality. The transport
sector changes the cone and mass along with the operators, preserving their weights.

## Development evidence

Development runs and their exact attempted source snapshots are preserved under
`evidence/development18`. Failed elaborations and strict linter diagnostics precede
successful final compiles. The production statements were not weakened. Development
objects reused authenticated predecessor objects and do not replace cold gates.
All eleven new negative fixtures passed expected rejection in a separate preflight.
The exact rational checker passed its declared exhaustive grids and boundary cases.

## Acceptance obligations

Run complete `final18` and `fresh18` gates sequentially, the latter from the frozen
source ZIP extracted without project proof objects. Preserve the 45-second command
limit, the full inherited control suite, actual axiom audit and kernel replays.
Compare all production objects and input identities. Any failure or interruption
remains distinct from a successful proof run. Update release status only after
terminated gates, comparison, clean extraction and full delivery verification.

## Next selected source target

Core 3.2, `r:occupancy`: prove correction signatures and occupancy records distinguish
exactly the same candidate subsets, exhibit every attainable occupancy, construct
the bijection, and derive the exact 2^r count and fixed-binary r-bit lower and upper
bounds. The evidence events must be exactly unions of the given nonempty partition
cells. The empty candidate set, unused target values and cells meeting several
target fibres all matter. Do not promote this result without its own formal gates.
''',encoding='utf-8')
(R/'CONTINUE_HERE.md').write_text('''# Continue from the accepted receipt, not a provisional heading

First read `release/ADMISSION_RECORD.json`, `release/REPORT.md` and
`release/ACCEPTED_PROGRESS_LEDGER.md` if supplied. They identify actual terminated
gates. This root preparation record and the configured theorem map are not evidence
that a run has completed. The previous verified state is 25/27 through Core 2.4.

Core 2.5 has two required sectors: the general convex-cone mixture and positive
idempotents on the finite coordinate cone. The new modules and direct raw API cover
both. See `docs/CORE25_PROOF_GUIDE.md` and `docs/CORE25_CORRESPONDENCE_AUDIT.md`.

After successful admission of Core 2.5, continue with Core 3.2. Locate the unchanged
source label `r:occupancy` and its preceding partition-evidence setup. Reuse the
existing `Correction.lean` signatures and minimal-cardinality theorem. Keep an
exact correspondence with unions of partition cells, not an enlarged evidence
language. Record a complete-source audit, negative controls and fresh gates.

The complete monograph is not a claim of full formalization. The Large Signal
Model's separate 39/87 correspondence and other specialist projects remain outside
this selected 27-result map.
''',encoding='utf-8')
(R/'docs/CORE25_PROOF_GUIDE.md').write_text(r'''# Core 2.5 — proof guide and correspondence

## Source and mathematical types

The immutable anchor is `source/core_v0.2.tex`, label `r:positive-packets`, original
printed page 6 and its setup immediately preceding the statement. The exact source
index and bindings are retained. The manuscript treats a real vector space, a
convex cone K, a linear mass λ strictly positive on K \ {0}, and a finite complete
family of linear packet operators preserving K.

`ConvexCone ℝ V` supplies actual closure under addition and positive scalar
multiplication. Its library definition does not force nonemptiness or zero
membership. This is sufficient: a normalized input is separately required to
belong to the cone; normalization uses a strictly positive inverse scalar. Thus no
extra pointedness, closedness, finite-dimensionality or coordinate positivity is
silently added. Strict mass already rules out nonzero zero-mass cone members.

## The general mixture

`StrictMass C mass` is exactly positivity on nonzero cone members.
`Preserves C P` checks actual image membership, not a name or intended property.
`Complete P` is equality of the finite sum of the supplied operators with the
identity. `IsState C mass v` asserts both cone membership and mass one.

For each index i, `weight mass P v i = mass (P i v)`. Cone preservation and strict
mass prove nonnegativity, and zero weight is equivalent to the zero packet.
Linearity carries completeness to the sum-of-weights identity. The positive index
subtype contains exactly the normalizable packets. Scaling by the inverse weight
preserves the cone and gives mass one. Multiplication by the original weight
recovers the packet. Finally the omitted terms vanish, so the restricted sum still
reconstructs v and its weights still sum to one.

Principal endpoint: `Komorebi.MachineTheory.PositivePackets.source_core25`.
The separate endpoint `sum_positive_weights_one` states the active-weight sum.
No idempotence or orthogonality appears in this sector. Positive halves of the
identity form a checked complete mixture even though neither half is idempotent.

## Coordinate classification

`Coordinate.cone N` is the actual coordinatewise nonnegative cone on `N → ℝ`.
`coefficient P r c` is obtained by applying P to the standard basis vector at c,
then evaluating coordinate r. `basis_expansion` and `coordinate_action` establish
the link to an arbitrary vector, rather than assuming a matrix representation.

Preserving the cone is equivalent to every coefficient being nonnegative.
Completeness says the coefficient sums are those of the identity. Nonnegative
terms summing to zero force all off-diagonal entries to vanish. Hence each map is
diagonal. Its idempotence then makes each diagonal coefficient d satisfy d²=d,
and the real-field identity implies d=0 or d=1. The diagonal sum being one gives
exactly one owner for every coordinate. The constructed owner map represents the
original operators as coordinate selectors. Different owners have disjoint ranges
and their cross compositions are zero.

`source_core25_coordinate` returns that concrete representation, unique ownership
and disjoint composition. `classification_iff` also proves every such selector
family is positive, complete and idempotent. Thus the result is a characterization,
not only a necessary condition. No positive coordinate dimension, nonempty index
type, pairwise-orthogonal assumption, or surjective ownership assumption is added.
An index may own no coordinates and represent the zero operator.

## Coordinate changes

For a linear equivalence e, `Transport` pushes the cone forward, pulls the mass
back by e⁻¹, and conjugates the packet maps. It proves preserved state membership,
strict mass, completeness, idempotence where supplied, equality of weights, and
equality of normalized packets after applying e. `source_coordinate_change`
collects the hypotheses needed to apply the general mixture theorem in the new
coordinates. It is not a theorem that signed coordinates are valid in the old
coordinate cone with the old mass left unchanged.

A real shear sends a normalized nonnegative state to (-1,1). It belongs to the
transported cone and has unit transported mass, despite its negative first
coordinate. The Haar detail example is different: it remains outside the declared
positive cone and has zero mass without vanishing. Coordinate signs alone cannot
replace the cone and mass contract.

## Source-facing checks and boundaries

`checks/CheckPositivePacketsAPI.lean` checks the source theorem from raw linear
maps, pointwise membership hypotheses, actual operator-sum equality and normalized
input. It independently checks the coordinate result from raw nonnegative inputs,
without assuming the bundled definitions as conclusions.

Eleven negative fixtures test omitted strict mass, omitted cone preservation,
omitted completeness, nonunit input, zero-packet normalization, non-idempotent
positive halves, overlapping projectors, incorrect coordinate-sign inference and
an unchanged mass after coordinate transport. They must fail for the expected
proof diagnostics, not name-resolution errors, missing imports or timeouts.

These declarations establish mathematical constructions. Some use classical choice
and are noncomputable. They do not certify a learned representation, numerical
stability, a physical probability model, or the Python checker in all executions.
The standard axioms and recorded Lean/dependency environment remain trusted.
''',encoding='utf-8')
(R/'docs/CORE25_CORRESPONDENCE_AUDIT.md').write_text('''# Core 2.5 source/statement review

This is an additional source-and-proof inspection in the same assistant session,
not an independent external referee or separate proof kernel.

| Source clause | Actual formal route | Boundary retained |
|---|---|---|
| Real vector space and convex cone | `ConvexCone ℝ V`, actual cone membership | No ambient dimension or closedness added |
| Strict positivity of mass | `StrictMass` and `mass_zero_iff` | Not mere nonnegativity |
| Finite complete maps | `Fintype I`, `Complete` | No countably infinite sums |
| Nonnegative weights and total one | `weight_nonneg`, `sum_weights_one` | Input has mass one |
| Positive normalized components | `PositiveIndex`, `normalized_isState` | No inverse-zero normalized state |
| Zero weights vanish | `weight_zero_iff` | Requires actual cone preservation |
| Exact mixture reconstruction | `mixture_reconstruction` | Every omitted term is proved zero |
| Standard-cone idempotents | `Coordinate.classification_iff` | Coordinate cone and idempotence explicit |
| Disjoint coordinate selection | `source_core25_coordinate` | Derived, not assumed |
| Coordinate dependence of signs | `Transport`, real shear example | Cone and mass change together |

The source propositions and proof text remain byte-identical. The formalization
has separate endpoints for the two source sectors. The raw API checks their joint
coverage. The theorem map also includes covariance as supporting material, not an
additional source-result count. The empty-coordinate example and empty-index
normalization impossibility prevent accidental strengthening by positivity of
cardinality. No claim of full-book formalization follows from this one admission.
''',encoding='utf-8')
print('Pre-gate documentation written')
