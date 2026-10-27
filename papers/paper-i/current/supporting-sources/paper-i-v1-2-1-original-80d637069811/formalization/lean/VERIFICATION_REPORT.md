# Komorebi Lean verification report

Author: Komorebi P.  
Lean component: v1.0.1  
Manuscript release: *Projector-Resolved Seed Calculus I*, v1.2.1  
Verification date: 2026-09-03

## Outcome

The aggregate Lean 4/Mathlib project builds successfully. The revised Paper I
completion contract has 35 rows, and every row is matched by an exact or
stronger compiled declaration at the explicit scope recorded in
[`LEAN_THEOREM_MAP_v1.0.1.md`](LEAN_THEOREM_MAP_v1.0.1.md).

The completion status is therefore **35/35 for the revised,
certificate-explicit contract**. This denominator does not include classical
existence or classification theorems that construct the certificates accepted
as hypotheses by rows 10, 13, 14, 32, and 35.

| Contract rows | Verified subject | Scope summary |
|---:|---|---|
| 1–9 | Free presentations and seed-rank operations | Algebraic quotient presentations; unrestricted cardinal cyclicity; semilinear monotonicity; image-algebra invariance; product and algebraic tensor bounds; scalar-quotient obstruction; the completion clause in row 1 assumes a dense continuous linear isometry into a Banach target. |
| 10–12 | Split semisimple formulas | Exact finite split-product, full-matrix, and multiplicity results from supplied algebra and compatible module equivalences. |
| 13–14 | One-operator formulas | Exact consequences of displayed primary/block-generation, polynomial-extraction, scalar-quotient, multiplicity, and minpoly/charpoly bridge certificates. |
| 15–25 | Packet coordinates and block algebra | Exact finite dependent packet coordinates, packetwise equality, bounded finite-product topology, closure of bounded-idempotent images of dense submodules, reconstruction, multiplication, powers, adjoints, full dependent block algebra, dimensions, and sharp algebraic support converses. |
| 26–30 | Reachability, transport, and realization | Algebraic reachability plus a separate bounded topological obstruction; conjugacy invariance; strict naturality; dense bounded realization; one typed finite quiver certificate. |
| 31–32 | Shift and graph models | The explicit bilateral reindexing representation has minimum finite dense seed cardinality one; graph rank is certificate-explicit in general, while the path and complex-cycle conclusions are unconditional at their recorded scopes. |
| 33–35 | Algorithm specifications | Mathematical termination and correctness of orbit-hull iteration and transfer-block tables, plus a certificate-driven exact graph seed-rank specification. |

## Component v1.0.1 modules

Six completion modules close the revised contract. Component v1.0.1 also adds
literal canonical-class evaluation theorems for the row 1 and 2 quotient
presentations and hardens the release audit without widening the mathematical
scope:

| Module | Principal coverage | Exact boundary |
|---|---|---|
| `SeedRankOperations.lean` | Rows 2–9 | Algebraic modules and cardinal/natural minima; the tensor theorem is algebraic over the stated scalar tower, not a completed topological tensor product. |
| `SemisimpleCompletion.lean` | Rows 10–12 | Split finite products with positive block sizes and supplied compatible equivalences; no Wedderburn–Artin existence proof or nonsplit division-algebra classification. |
| `SingleOperatorGraph.lean` | Rows 13, 14, 32 | Lean verifies primary/Jordan-style and spectral conclusions from explicit certificates; it does not derive those certificates from an arbitrary operator or symmetric matrix. Path and complex-cycle minimum results are separately unconditional. |
| `PacketNaturalityCompletion.lean` | Rows 16, 21, 23–28, 30 | Finite algebraic packet families, dependent block maps, strict typed transport, and the stated quiver model; no infinite sum or general bounded-category support converse. |
| `TopologicalCompletion.lean` | Topological parts of rows 1, 17, 18, 22, 26, 29, 31 | Normed/Banach and bounded-operator hypotheses are explicit; row 18 holds for any bounded idempotent (with a packet-family specialization), the packet isomorphism uses the canonical finite dependent-product norm, and the shift theorem concerns the explicit integer reindexing grammar. |
| `EllipticAlgorithms.lean` | Rows 33–35, plus the algebraic elliptic example | Algorithm theorems are mathematical specifications. Exact graph rank consumes supplied certificates. The elliptic declarations prove algebraic coordinate/operator identities only. |

The pre-existing modules continue to supply the projector core, exact packet
coordinates, fibre and residue refinement, typed block transport,
operator-level reconstruction and composition, seed-rank basics, the one-block
semisimple calculation, full-matrix cyclicity, and the endpoint path Krylov
certificate.

## Build and kernel audit

Commands:

```bash
lake --wfail build
python scripts/verify_theorem_map.py
lake env lean -E warning KomorebiVerification/KernelAudit.lean
```

All three commands exit successfully. The warning-fatal public aggregate build
completed all **8,883 jobs** without a warning. Narrow file-level suppressions
cover only legacy style/unused lints in unchanged proof bodies; any unsuppressed
warning fails the build.

`scripts/verify_theorem_map.py` enforces exactly 35 contiguous rows, accepted
`Exact`/`Stronger` classifications, 84 unique declaration references, compiled
existence of all 84 names, synchronized release/map versions, and exact set
equality with the 84 direct `#print axioms` commands in `KernelAudit.lean`.
The final namespace-wide command then traverses all **1,126** compiled
`Komorebi.*` and `KomorebiVerification.*` declarations and fails compilation
on a project axiom, explicit opaque constant, unsafe declaration, `sorryAx`, or
any axiom outside Lean/Mathlib's standard foundations:

```text
propext
Classical.choice
Quot.sound
```

No project-specific axiom, `sorryAx`, theorem placeholder, `admit`, unsafe
declaration, or opaque proof escape is part of the checked component. The audit
is not imported by the public aggregate; release runners invoke it explicitly
as a separate mandatory gate.

## Certificate and implementation boundary

The kernel checks implications from precisely typed hypotheses. In particular:

- the split semisimple theorem consumes chosen algebra and module
  equivalences; it does not construct a Wedderburn decomposition;
- the single-operator and four-way cyclicity theorems consume the displayed
  primary/block, polynomial, quotient, multiplicity, and canonical-form
  bridges; they do not construct Jordan form;
- the general graph theorem consumes eigenbasis/projector or distinct-spectrum
  data; it does not derive diagonalizability from symmetry;
- `exactGraphSeedRank` consumes verified exact spectral certificates and is
  noncomputable; there is no verified eigensolver, factorization routine, code
  extraction, runtime bound, or performance claim;
- the orbit-hull and transfer-block algorithms are mathematical
  termination/correctness specifications, not extracted basis-maintenance or
  sparse-graph programs;
- the affine cubic example checks its quotient-coordinate normal form,
  projectors, multiplication identities, and unit-seed algebra. It does not
  prove projective smoothness, genus, or that a displayed scalar is the
  geometric discriminant.

These exclusions are part of the theorem-completion statement, not deferred
claims of this report.

## SHA-256 source inventory

The following hashes were computed from the frozen v1.2.1 release files. They
cover the aggregate import, every Lean source module, the theorem map, and its
executable checker.

```text
292bc683670b4cec1c82c52d643a54fd6dd3598681401cdc451f52bc5b78b8bf  KomorebiVerification.lean
41aa765635e8e80eca2181f1de37763aed08f14cd608941a1bd01c247370aeb9  KomorebiVerification/Basic.lean
600f7cb3362e319c842eb3767c7afc88f914a757b5e25a041d94acf1bbf4ff62  KomorebiVerification/EllipticAlgorithms.lean
fd7e87c13e0a3dcc2f990db751f81c759548cbcbc62338d8b66dc69aa9c86739  KomorebiVerification/ExactCoordinates.lean
f448d54154ac8a1c2e4c941242afb08de9a19e361bc12f6a222595f61eb1a8a9  KomorebiVerification/FibreRefinement.lean
0b89e53af5d4d18762ca8055c0e17820e29a8686b3208cdd3c0bdff8218d832d  KomorebiVerification/FullMatrixCyclicity.lean
654651d3547abf1fd4a9053b886cd5bc46ef6ddb0ceb903f239a4ae5f52d7573  KomorebiVerification/KernelAudit.lean
abac4f683fdf13b7a103fda2117398231aef35505e0bac6174a364d2cd0c8801  KomorebiVerification/PacketNaturalityCompletion.lean
498cd76bbe95b3bfd5922ad25d223a820e3a923f679005e931ff1621f1d9afeb  KomorebiVerification/PaperIBlockCompletion.lean
3c59b354f59871e1540d64d461a3bbc6f443f1380d29d30d998de4187ea2b29e  KomorebiVerification/PaperITransport.lean
8fff9933d4418b47df0daafd7ebd43a8af07cd7a6a43c8d30a830be43dfbd976  KomorebiVerification/PathGraphKrylov.lean
d69e499f2ae86f673292022895a234349dad40da960897e790a4511c3aeede0d  KomorebiVerification/ProjectorCore.lean
987899e7a6827501ae15fb0167dc2df3edb74e70d316752ccfe12c4f3ba89f41  KomorebiVerification/ResidueProjectors.lean
3efef4e4e173500bea53a2da70e3ecdaad82e392f869a0bfa590e16f3f554571  KomorebiVerification/SeedRankBasics.lean
4576e26fbc1dc4c9c03a72c3c6e13aca95022950d5592bfa8bd415bb898e917b  KomorebiVerification/SeedRankOperations.lean
a3602596f498757fd1eec773c28288adbf733b41b06bd8ab0ce8b19fe49d9e0b  KomorebiVerification/SemisimpleCompletion.lean
9c0ff0f5842f51892107ed604e7e6182c38c780b1a728b088db1bbf8687240c2  KomorebiVerification/SemisimpleSeedRank.lean
8717b60b80fed96d15c89594cffd7ce505eece6f765d935c3a915ede81fa48bd  KomorebiVerification/SingleOperatorGraph.lean
e7d332c4b9d3b32dbb0efa368263363cda40ab77e2b8cd2ffbf398f85d3009f0  KomorebiVerification/TopologicalCompletion.lean
a799309f0aae94a70b008f42c2aefddd54accb06442f155413e7d3fbc3f29e17  LEAN_THEOREM_MAP_v1.0.1.md
20de9655acc0217044b2787e46564e3bdbda3c3cf636f3bc121dd6075f212ec6  scripts/verify_theorem_map.py
```

## Final scope statement

Component v1.0.1 verifies the declarations imported by this project and the
35 revised manuscript statements mapped to them. It does not establish bare
classification theorems, certificate construction, executable numerical
software, performance, elliptic-curve geometry, historical novelty, or global
universality assertions.
