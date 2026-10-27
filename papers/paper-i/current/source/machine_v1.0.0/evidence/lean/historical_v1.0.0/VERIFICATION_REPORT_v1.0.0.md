# Komorebi Lean verification report

Author: Komorebi P.  
Lean component: v1.0.0  
Manuscript release: *Projector-Resolved Seed Calculus I*, v1.2.0  
Verification date: 2026-09-03

## Outcome

The aggregate Lean 4/Mathlib project builds successfully. The revised Paper I
completion contract has 35 rows, and every row is matched by an exact or
stronger compiled declaration at the explicit scope recorded in
[`LEAN_THEOREM_MAP_v1.0.0.md`](LEAN_THEOREM_MAP_v1.0.0.md).

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

## Component v1.0.0 modules

Six completion modules close the revised contract:

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
lake build
lake env lean KomorebiVerification/KernelAudit.lean
```

Both commands exit successfully. The aggregate build completed all **8,884
jobs**. Lean emitted non-fatal style/linter warnings, including legacy style
suggestions and unused-variable diagnostics; it emitted no build error.

`KernelAudit.lean` imports all six completion modules and runs `#print axioms`
on representative principal declarations across every contract section. The
reported dependencies are limited, as applicable, to Lean/Mathlib's standard
foundations:

```text
propext
Classical.choice
Quot.sound
```

No project-specific axiom, `sorryAx`, theorem placeholder, `admit`, unsafe
declaration, or opaque proof escape is part of the checked component.

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

The following hashes were computed from the frozen v1.2.0 release files. They
cover the aggregate import and every Lean source module in the component.

```text
4cdedc2ed5d3b5a5e7ce02ce267d73b1d04ad05d04e9ff66b5e5fa4c05fb15a9  KomorebiVerification.lean
41aa765635e8e80eca2181f1de37763aed08f14cd608941a1bd01c247370aeb9  KomorebiVerification/Basic.lean
08c5f19924e90e2ce1b8c77fbbd764c3017b86114b987b6b0d22272e9924f3d4  KomorebiVerification/EllipticAlgorithms.lean
fd7e87c13e0a3dcc2f990db751f81c759548cbcbc62338d8b66dc69aa9c86739  KomorebiVerification/ExactCoordinates.lean
f448d54154ac8a1c2e4c941242afb08de9a19e361bc12f6a222595f61eb1a8a9  KomorebiVerification/FibreRefinement.lean
0b89e53af5d4d18762ca8055c0e17820e29a8686b3208cdd3c0bdff8218d832d  KomorebiVerification/FullMatrixCyclicity.lean
bc531247e936f07ad61adaad5b03df005d7f4f0d2a80e85aa5a6ac245244a029  KomorebiVerification/KernelAudit.lean
dd2dd87510057f643ad3878479ee42051606f85a3fd452f60de54dd12ff8be62  KomorebiVerification/PacketNaturalityCompletion.lean
498cd76bbe95b3bfd5922ad25d223a820e3a923f679005e931ff1621f1d9afeb  KomorebiVerification/PaperIBlockCompletion.lean
3c59b354f59871e1540d64d461a3bbc6f443f1380d29d30d998de4187ea2b29e  KomorebiVerification/PaperITransport.lean
8fff9933d4418b47df0daafd7ebd43a8af07cd7a6a43c8d30a830be43dfbd976  KomorebiVerification/PathGraphKrylov.lean
41775abb0c089d315b4afd8815b04122d19c1be1c256b50be89b6e88bdfcff17  KomorebiVerification/ProjectorCore.lean
987899e7a6827501ae15fb0167dc2df3edb74e70d316752ccfe12c4f3ba89f41  KomorebiVerification/ResidueProjectors.lean
85f4cace3f2275a43d05fa0566f304bce49b6e15a0068f6ffed48f67fe88d475  KomorebiVerification/SeedRankBasics.lean
35628709c1dea94050948ddd0b878302bf2466e54d5184f8e99bcd685c1561f0  KomorebiVerification/SeedRankOperations.lean
7cba962cf8a7a7ac7de79524ba6b6179fa3236f1159bd8b4f101d33b6e307e1c  KomorebiVerification/SemisimpleCompletion.lean
9c0ff0f5842f51892107ed604e7e6182c38c780b1a728b088db1bbf8687240c2  KomorebiVerification/SemisimpleSeedRank.lean
8717b60b80fed96d15c89594cffd7ce505eece6f765d935c3a915ede81fa48bd  KomorebiVerification/SingleOperatorGraph.lean
e7d332c4b9d3b32dbb0efa368263363cda40ab77e2b8cd2ffbf398f85d3009f0  KomorebiVerification/TopologicalCompletion.lean
```

## Final scope statement

Component v1.0.0 verifies the declarations imported by this project and the
35 revised manuscript statements mapped to them. It does not establish bare
classification theorems, certificate construction, executable numerical
software, performance, elliptic-curve geometry, historical novelty, or global
universality assertions.
