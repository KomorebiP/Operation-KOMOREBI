# Changelog

## 1.2.1 — 2026-09-03

Audit-hardening, provenance, and figure-correction revision. The archived
v1.2.0 and earlier artifacts are not modified.

### Formal verification

- Promoted the Lean component to v1.0.1 and added literal quotient-evaluation
  glue theorems for the one-seed and multi-seed presentation rows.
- Expanded the direct axiom report from representative declarations to all 84
  unique declarations in the 35-row theorem map.
- Added an executable theorem-map checker that enforces row continuity,
  accepted classifications, declaration uniqueness and existence, synchronized
  release metadata, and exact equality with the direct audit list.
- Added a namespace-wide fail-closed audit of 1,126 compiled project
  declarations. It rejects project axioms, explicit opaque constants, unsafe
  declarations, `sorryAx`, and any nonstandard axiom dependency.
- Removed the audit module from the public aggregate so importing the library
  has no diagnostic side effects; both release runners execute the audit as a
  separate mandatory gate.
- Made the aggregate build warning-fatal, with narrowly documented suppression
  only for legacy style and unused-variable lints whose proof terms remain
  unchanged.

### Reproducibility and presentation

- Promoted the Python companion to v1.1.1 because its figure generator changed.
- Separated manuscript release `1.2.1` from Python companion `1.1.1` in both
  machine-readable result records.
- Repaired connector/label collisions in the grammar and theorem-dependency
  diagrams on manuscript pages 5 and 32.
- Replaced in-place verification with isolated-copy `Run_All.ps1` and
  `Run_All.sh` runners so verification cannot alter canonical release members.
- Fixed the default artifact epoch at `SOURCE_DATE_EPOCH=1788393600`; repeated
  clean figure, wheel, and manuscript builds are byte-reproducible.
- Removed an unrelated internal `v1.2.2` label from the formal core banner.

## 1.2.0 — 2026-09-03

Lean-completion and manuscript scope-alignment revision. The archived v1.1.0 and v1.0.0 artifacts are not modified.

### Formal verification

- Promoted the Lean component to v1.0.0 and imported declarations covering all 32 revised named statements and all three mathematical algorithm specifications.
- Added seed-rank operations, split-semisimple assembly, certificate-explicit single-operator and graph results, packet/naturality completion, the topological branch, the bilateral shift, elliptic coordinates, and finite algorithm correctness specifications.
- Completed the aggregate build and principal-declaration axiom audit with no `sorry`, `admit`, `sorryAx`, project-specific axiom, unsafe declaration, or explicit opaque substitute.

### Scope alignment

- Made decomposition and exact spectral certificates explicit where Lean verifies the resulting theorem but not the classical classification or eigensolver that supplies the certificates.
- Restricted topological packet coordinates to the standard finite product norm and stated the boundedness, completeness, and closure hypotheses used by the checked declarations.
- Distinguished mathematical algorithm specifications from executable extraction and performance claims.
- Kept elliptic smoothness, genus, and the geometric discriminant interpretation as cited background rather than Lean-checked algebraic conclusions.

### Release engineering

- Added the 35-row completion contract and exact declaration map.
- Carried forward the Python v1.1.0 companion unchanged; this revision changes the manuscript and Lean component.

## 1.1.0 — 2026-09-02

Correctness, attribution, formal-verification, and reproducibility revision. The archived v1.0.0 artifact is not modified.

### Mathematical repairs

- Defined seed rank as a cardinal-valued minimal generator invariant and fixed the zero-space convention.
- Corrected image-algebra invariance and the typed naturality theorem by separating source and target operators and packet labels.
- Removed the unnecessary openness assumption from dense realization.
- Repaired the tensor-product proof with the required finite double sum.
- Stated the finite-quiver, Banach-completion, boundedness, nonzero-packet, and field/characteristic hypotheses where they are used.
- Distinguished algebraic full-block maps from bounded block maps.
- Corrected the typed quiver obstruction to the unreachable subspace `ker B`.
- Typed the elliptic packet matrix through coefficient coordinates and corrected the operator relation.
- Replaced a finite path-graph observation by an all-size combinatorial proof; the result is also Lean-checked.
- Clarified cycle multiplicities and classified all reported graph computations as finite sampled ranges.

### Evidence and attribution

- Added a nine-item local bibliography with verified DOI links.
- Added a 35-row claim-status ledger separating paper proof (`P`), classical input (`C`), finite computation (`I`), and scoped Lean verification (`L`).
- Added a formal-verification section tied to concrete Lean modules and declarations.
- Integrated Lean tranche v0.3.0, including cardinal seed rank, quotient results, one-block multiplicity, full-matrix cyclicity, exact packet coordinates, transport, block identities, support converses, and all-size path cyclicity.

### Reproducibility and release engineering

- Moved the release to one canonical `paper/`, `code/python/`, `formalization/lean/`, `results/`, and `provenance/` layout.
- Updated the Python package to v1.1.0 and made the experiment pipeline regenerate JSON, CSV, figures, and a hashed run record.
- Added exact dependency resolution for the tested CPython 3.12 environment.
- Made the PowerShell runner fail on missing required tools and capture Python, test, wheel, Lean, and LaTeX logs.
- Added citation metadata, release metadata, license status, a canonical manifest, checksums, and an external archive checksum.

## 1.0.0

Initial Paper I release. Its archived ZIP has SHA-256 `9058efe66ad7ed7578a98340f0966dfd865ac627ee8426ecdc69acacf3c28c72`.
