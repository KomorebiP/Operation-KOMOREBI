# Source and Claim Map — Paper I v1.2.1

Author: **Komorebi P.**  
Release date: **2026-09-03**

## Evidence classes

- **P — paper proof:** a proof appears under the displayed hypotheses; this does not imply novelty.
- **C — classical/reformulated:** the result relies on established module, matrix, topological-vector-space, elliptic-curve, or graph-spectral theory cited in the manuscript.
- **I — implementation certificate:** exact finite computation, finite sampled range, or floating-point regression.
- **L — Lean-checked scope:** only the certificate-explicit declaration scope named in the paper, completion map, and formal verification report.

The paper contains the authoritative 35-row claim-status ledger. No Paper I theorem depends on a conjecture.

## Material revisions in v1.2.1 from v1.2.0

- The Lean component advances to v1.0.1. Rows 1 and 2 gain literal quotient
  evaluation glue, while the scoped mathematical claims remain unchanged.
- The executable theorem-map checker enforces all 35 rows and all 84 unique
  mapped declarations, including a one-to-one direct axiom-report list.
- The fail-closed audit traverses every compiled project declaration and rejects
  project axioms, explicit opaque constants, unsafe declarations, `sorryAx`,
  and nonstandard axiom dependencies.
- The public aggregate no longer imports the diagnostic audit module; the
  non-mutating release runners execute it explicitly after a warning-fatal build.
- Both runners use a fixed default `SOURCE_DATE_EPOCH`; repeated clean figure,
  wheel, and manuscript builds are byte-reproducible.
- The Python companion advances to v1.1.1 for corrected diagrams and explicit
  manuscript-versus-companion provenance fields. The mathematical numerical
  routines and finite sample scopes are unchanged.
- Connector/label collisions in Figures 1 and 10 are corrected.

## Historical v1.2.0 revisions from v1.1.0

- The Lean component advances to v1.0.0 and covers all 35 rows of the revised completion contract.
- Decomposition and exact spectral certificates are explicit hypotheses where the checked theorem uses classical Wedderburn, Jordan, or spectral input.
- Topological packet coordinates use the standard finite product norm, and the checked completion, closure, boundedness, and dense-realization hypotheses are stated explicitly.
- The bilateral-shift result uses the concrete integer-power grammar on `ℓ²(ℤ,K)` and proves minimum finite seed number one.
- The three algorithm rows are mathematical correctness specifications; executable extraction, eigensolver verification, and performance are not asserted.
- Elliptic smoothness, genus, and the geometric discriminant interpretation remain cited background outside the Lean-checked algebraic coordinate theorem.
- The Python v1.1.0 companion and its finite implementation evidence are carried forward unchanged.

## Historical v1.1.0 revisions from v1.0.0

- Seed rank is cardinal-valued, with seed rank zero for the zero module.
- The universal completion statement uses a pulled-back Hausdorff topology and explicit completeness/continuity assumptions.
- Isomorphism invariance is stated over the image algebra unless the algebra map is onto.
- The tensor proof uses finite double sums.
- Naturality now distinguishes source and target packet systems, labels, and operators.
- Dense realization requires continuity and surjectivity but not openness.
- Algebraic and bounded full-block statements are separated.
- The quiver obstruction is the nonzero subspace `ker B` unreachable from seeds supported at `U`.
- The elliptic model assumes characteristic not two, types the coefficient coordinates, and states the correct operator relation.
- The bilateral shift specifies real or complex scalar field.
- Path endpoint cyclicity and determinant one are proved for every nonempty finite path; the cycle result is stated through maximum eigenspace multiplicity.
- All finite graph ranges and full-matrix samples are described as samples.

## Lean component v1.0.1

Kernel-checked source covers all 32 revised named statements and all three mathematical algorithm specifications under the exact hypotheses recorded in the declaration map. In particular, it covers:

- cardinal seed rank, quotient and image-algebra transport, direct sums, tensor products, and scalar-quotient obstructions;
- split-semisimple assembly under chosen algebra/module equivalences, full-matrix cyclicity, and multiplicity obstructions;
- single-operator and spectral graph formulas from explicit primary, polynomial, eigenbasis, and projector certificates, together with unconditional path and cycle corollaries;
- exact algebraic and bounded packet coordinates, reconstruction, multiplication, powers, adjoints, full-block algebras, support, reachability, transport, and strict naturality;
- dense-isometric completion, finite packet completion, bounded dense realization, the typed-quiver certificate, and the concrete bilateral shift;
- the algebraic elliptic coordinate model and proved finite mathematical specifications for the orbit-hull, transfer-block, and exact graph-rank algorithms;
- the earlier fibre/refinement, residue-projector, weighted-difference, and coefficient-section declarations imported by the aggregate project.

The classification or spectral data consumed by certificate-explicit theorems are not themselves constructed by Lean. The checked scope also excludes a verified eigensolver, executable extraction, performance guarantees, elliptic smoothness or genus, the geometric interpretation of the discriminant, and any claim of historical novelty or priority.

## Python evidence

The Python v1.1.1 companion, its 18 tests, and the `results/` artifacts exercise the finite implementation. Symbolic integer/polynomial outputs are distinguished from finite sampled graph ranges and floating residuals. The result records separately identify manuscript release v1.2.1 and companion version v1.1.1. In particular, two tested full-matrix seeds do not computationally quantify over every nonzero vector; that theorem is established in the paper and Lean instead.

## External boundary

The release has internal proof, build, test, kernel, and visual checks. Independent peer review and a comprehensive historical-priority search remain external work.
