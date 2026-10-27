# Komorebi Physics Lean v0.2.0 — Checked Block 02

**Cumulative verification: PASS.**

| Measure | Verified count |
|---|---:|
| New Block 02 theorem declarations | 51 |
| Unchanged Block 01 new theorem declarations | 37 |
| Preserved Paper VII theorem declarations | 39 |
| Total active theorem declarations | 127 |
| Active mathematical modules | 10 |
| Audited named declarations | 160 |
| Invalid controls correctly rejected | 9 / 9 |

The new modules are `Deformation` (24 theorems), `MovingAtlas` (16), and `DeformationExamples` (11). They also contain 13 definitions, including the proof-bearing `transportedFamily` and `unitaryAtlas` constructions. Definitions are not counted as theorems.

## Newly checked

Chapter 2.6: the actual inverse derivative, moving-projector commutator derivative, full three-term corner derivative, covariant reformulation, reconstruction cancellation, and finite coarsening compatibility. The main inverse result uses completeness and invertibility at the base point, not an assumed inverse derivative.

Chapter 2.5: actual bounded-operator moving coordinates on arbitrary-dimensional complex Hilbert spaces, differentiated unitarity, skew connection and effective generator, construction of the transported orthogonal atlas, and actual packet-energy derivatives in both moving and laboratory coordinates.

Exact witnesses: a nonconstant invertible shear, a nonstationary moved idempotent, three nonzero corner-rate terms, failure of all single-term omissions, wrong commutator sign, and a nonunitary similarity that is not self-adjoint.

## Evidence

The final run completed at **2026-09-13T17:15:10.270420+00:00**, in **88.18 seconds**. It freshly compiled all ten mathematical modules and the aggregate import. Ordinary Lean axiom commands were run in ten module batches and cover the exact 160-name inventory. All reported dependencies are in `propext`, `Classical.choice`, `Quot.sound`. Both upstream preservation and all seven Block 01 source-preservation checks passed.

Compiler: Lean 4.34.0-rc2. Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency commits and tracked source trees were checked. Local source hashes were checked before and after verification; negative-control inputs were included in those hashes. The imported dependency cache was used, not rebuilt wholesale.

## Boundaries

This is not a proof of all 550 pages. Chapter 2.5–2.6 now have checked representatives in the declared bounded-operator / finite-atlas setting. Flow existence, strong-only differentiability, countable sums, unbounded operator domains, later variational and continuum claims, gravity, and cosmology are not established by this block. No percentage of full-edition completion is asserted.

“51 new” means newly authored formal declarations in this block, not 51 independent new physical laws.

## Failures and repairs

The first baseline cumulative run was interrupted by the outer execution deadline during its axiom audit. It is retained as INTERRUPTED and never counted as a pass. A smaller-batch audit subsequently completed. Development also encountered hidden imported definitions, function-expression normalization errors, unused-hypothesis warnings, a deprecated lemma name, a namespace collision, and an unsuitable default matrix-norm interface. The active proofs were repaired without admissions or custom axioms. Detailed failures and proof snapshots are retained.

## Next block

Chapter 4: state-dependent skew flow, associative refinement towers, and then mixed-state trace transfer. Chapter 3's physical-unit and later variational/asymptotic sequents remain separately inventoried targets, not consequences of this block.
