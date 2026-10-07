# Paper III v1.0.1 Verification Report

**Author:** Komorebi P.  
**Verification date:** 2026-09-03

## Environment

- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Lake 5.0.0
- Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Warnings promoted to errors by `moreLeanArgs = ["-E", "warning"]`
- Fixed release epoch: `1788393600` (`2026-09-03T00:00:00Z`)
- Python 3.12.13, Matplotlib 3.10.8, and Pillow 12.3.0 for figures
- pdfTeX 1.40.25, Poppler, and Ghostscript for PDF validation

## Final results

| Check | Result |
| --- | --- |
| Clean `lake --wfail build` | Pass; 3,076 jobs |
| Theorem-map parity gate | Pass |
| Theorem-map rows | 41 |
| Unique mapped declarations | 143 |
| Mapped theorem declarations | 88 |
| Mapped constructions | 55 |
| Supporting-only audit declarations | 0 |
| Unique explicit kernel-audit targets | 143 |
| Manuscript Paper III statuses | 42 invocations; 99 references; 99 unique |
| Inherited Papers I--II statuses | 6 invocations; 14 references; 12 unique |
| Fail-closed namespace audit | Pass; 468 declarations, including 229 theoremInfo declarations |
| Unproved-placeholder and forbidden-declaration scan | Pass |
| Deterministic figure regeneration | Pass, byte-identical; 3 figures |
| pdfTeX convergence | Pass; 4 passes |
| Deterministic PDF rebuild | Pass, byte-identical |
| PDF structural and font checks | Pass; all fonts embedded, no Type 3 fonts |
| CFF 1.2.0 schema validation | Pass |
| Final PDF | 27 pages |
| Full-document render inspection | Pass; all 27 pages inspected |
| Clean extracted-archive verification | Pass |
| Deterministic archive rebuild | Pass, byte-identical |

The explicit kernel reports contain only `propext`, `Classical.choice`, and
`Quot.sound`, or no axioms. The namespace gate independently rejects project
axioms, explicit opaque constants, unsafe declarations, `sorryAx`, and any
transitive axiom outside that standard basis.

## Scope verified

- Packet-supported edge products obey the stated source/target orientation;
  broken interfaces vanish and composable words reduce to endpoint blocks.
- Finite transfer powers have exact word, walk, and coefficient-level endpoint
  expansions, including fixed-length and orbit-support vanishing results.
- Exact coordinate transport and naturality are distinct from reversible
  connection data. Additive defect, triangle holonomy, flat reconstruction,
  finite path transport, and gauge covariance are compiled.
- Complete packet resolutions reconstruct the full holonomy obstruction;
  vanishing of all blocks is equivalent to vanishing of the obstruction, and
  a nonzero block yields a classical packet witness.
- The arbitrary-length heterogeneous expansion uses one common finite packet
  index. Differing intermediate index types are compiled separately at lengths
  two and three.
- Unary/binary operation trees satisfy input locality, and candidate-specific
  obstruction packets have the exact equivalence stated in the manuscript.

## Artifact record

| Artifact | SHA-256 |
| --- | --- |
| Final PDF | `dea6a4e1958c4deefd1646131705db6e500d1fd0905b74428b9b4a1a66de9843` |
| LaTeX source | `96750e95867c0c0bed17b8031e6190a237b33a5fde4388f09ff1d1289ce98d84` |
| Lean theorem map | `41c4d14674d14bfaabeab6c311e7a2ef1298f230fa776648402f50ee2df27866` |
| Kernel-audit transcript | `503d1a7ae975fadf3a2b44e3260eb19f81a22248c7044f6e5d7e1f2e044071bf` |
| `typed_edge_walks.png` | `a03832e99b8f829231229ef7c250efb45b9579203354895ef4735f3f2ae83410` |
| `transport_vs_connection.png` | `55405c4642a80c780cb987bba6646d26859a588cf42940c22b86d696fdb2b6e5` |
| `holonomy_obstruction_blocks.png` | `1c8359da5591a64c222ca398ec7a5a7a700277c605803cc2bf916740c249cbbc` |

## Boundary

The verification conclusion is scope-explicit: Paper III v1.0.1 is complete
for the finite algebraic contract in
`provenance/Lean_Completion_Contract.md`. It does not certify roadmap items,
novelty, priority, physical interpretation, or external peer review.

The separately verified Papers I--II v1.2.1 dependency bundle has SHA-256
`a20cf9353f0e882834d31e665dfd819a04e43fa606d402309be63e3b94447052`.
Clean-room Lean verification used the pinned dependency tree named by
`lake-manifest.json`; the release itself deliberately omits dependency and
build caches.
