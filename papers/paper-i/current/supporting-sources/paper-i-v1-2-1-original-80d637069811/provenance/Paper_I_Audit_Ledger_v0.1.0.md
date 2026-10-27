# Paper I audit ledger

**Paper:** *Projector-Resolved Seed Calculus I: Typed Seeds, Operator Grammars, and Exact Reconstruction*  
**Author:** Komorebi P.  
**Audit version:** 0.1.0  
**Audit date:** 2026-09-02  
**Manuscript audited:** 32-page release package created 2026-07-27 03:40 UTC

## Executive verdict

**Paper I survives substantive mathematical audit, but it is not yet ready for external publication.**

No fatal counterexample was found to its central finite-dimensional algebraic spine: module generation, finite complete projector coordinates, transfer-block reconstruction and multiplication, the split-semisimple generator formula, the single-operator formula, or the worked finite examples. The paper contains a strong and coherent foundational framework.

The current text nevertheless needs a controlled revision before its status should move beyond `internal_complete`. One tensor-product proof sentence is false as written; the naturality section contains a genuine typing error; several topological and infinite-quiver statements omit necessary hypotheses; two examples overstate what is unreachable or computationally tested; and the current release lacks the citations and immutable provenance expected of a standalone research paper.

The appropriate novelty claim at this stage is **framework architecture and synthesis**, not that the underlying module-generator formulas are all new. In standard algebraic language, seed rank is the classical minimal number of module generators, often written \(\mu_A(M)\). A theorem-by-theorem literature and priority review remains open.

## Artifact and reproducibility audit

| Item | Result |
|---|---|
| Current release archive | `Projector_Seed_Calculus_I_Release(1).zip` |
| Archive SHA-256 | `9058efe66ad7ed7578a98340f0966dfd865ac627ee8426ecdc69acacf3c28c72` |
| Current bundled TeX SHA-256 | `4ad6a0a0b66f37e6943ca136f4c9286e7881f2eac65e1c208460f238beb2867c` |
| Current bundled PDF SHA-256 | `3f35402f77de4a33ff1cc3ab4b54558bf109614901d96e8e1f03564403befa87` |
| Manifest verification | Every archived entry passed `sha256sum -c SHA256SUMS.txt` |
| Python tests | 18/18 passed; rerun time 0.93 s |
| Deterministic pipeline | `python run_all.py` regenerated ten figure pairs; stored JSON and CSV remained byte-identical |
| Stored JSON SHA-256 | `f1de54377728c4a4c82a6eb4c0e97ddd98eba4f058d3e9c6ee7a19793baef60d` |
| Stored CSV SHA-256 | `98c24ad7f4b690a2e2cbcf13eeca3e0f00dd6bb1d673cceb2c17395a1b63becf` |
| Audit environment | Python 3.12.13; NumPy 2.3.5; SymPy 1.14.0; Matplotlib 3.10.8; pytest 9.1.1 |
| PDF inspection | All 32 pages rendered and visually inspected; no clipping, overlap, missing glyphs, or broken figures/tables found |

The later release is treated as authoritative because it has the later creation time and removes packaging debris. Its code and tests match the earlier archive. Its manuscript removes the earlier six-item bibliography rather than adding in-text citations; this is cleaner as a series package but weaker as a standalone paper.

The release is reproducible at the source/test level, but not yet archival-grade. It should add a semantic version, repository or immutable release URL, commit/archive identifier, exact environment lock, license, citation metadata, and an explicit distinction between exact symbolic checks and floating-point diagnostics. The fixed RNG seed (`20260727`) and numerical rank tolerance (`1e-10`) appear in source but should also appear in the generated record.

## Claim ledger

Paper I contains 32 theorem/proposition/corollary environments, alongside 14 definitions, four constructions, four examples, four explicit boundaries, and seven remarks.

| Claim family | Mathematical verdict | Formal status | Required action |
|---|---|---|---|
| Universal and multi-seed presentations; cyclicity; quotient and isomorphism laws | Algebraically sound | Cardinal seed rank, quotient presentations, quotient monotonicity, equivalence invariance, and finite cyclicity are kernel-checked | State the more general algebra-homomorphism cases using image algebras or restriction of scalars |
| Shared/independent sums, tensor bound, scalar quotient obstruction | Conclusions sound | Not yet formalized | Replace the incorrect simple-tensor sentence with a double-sum expansion |
| Split semisimple multiplicity formula | Sound under finite-dimensional split semisimple hypotheses | One-simple-block theorem kernel-checked; finite-product assembly pending | State the field/splitting hypotheses at the theorem, not only in surrounding prose |
| Full matrix algebra and multiplicity obstruction | Sound | Every nonzero vector's full-matrix cyclicity and the one-block multiplicity theorem are kernel-checked | Mark the full matrix grammar as maximal rather than compressed |
| Single-operator formula and cyclic-matrix criterion | Sound for finite-dimensional spaces over an algebraically closed field | Not yet formalized | Add the zero-space convention or assume \(X\ne0\); state finite-dimensionality explicitly |
| Exact packet coordinates and packetwise equality | Sound for a finite complete orthogonal family | Fully kernel-checked in the algebraic setting | Make the finite index and completeness hypotheses visible in every summary statement |
| Topological packet isomorphism and completion | Intended result is sound with stronger hypotheses | Only the algebraic inverse laws are checked | Require Hausdorff complete topological vector spaces, continuous projectors/action, and the pulled-back Hausdorff topology |
| Transfer-block reconstruction and multiplication | Sound | Fully kernel-checked pointwise and as equalities of linear maps | No mathematical repair required |
| Packet powers and adjoint reversal | Sound with the expected finite/Hilbert hypotheses | Not yet formalized | State continuity/boundedness and orthogonal-projector hypotheses explicitly |
| Full block algebra and dimension count | Algebraically sound | Reconstruction/injectivity ingredients checked; full algebra equivalence pending | In topological categories, use continuous/bounded block maps rather than all linear maps |
| Support pattern versus preorder | Algebraic equivalence is sound over a nontrivial semiring | Identity/reflexivity and multiplication-closure/transitivity equivalences are kernel-checked for ordinary matrices | For the topological converse, require enough continuous rank-one maps/nontrivial continuous duals |
| Reachability obstruction | Sound for finite algebraic expressions | Not yet formalized | Require continuity before passing to topological closures |
| Coordinate transport and naturality | Conjugation idea sound; manuscript statement is ill-typed | Corrected coordinate-conjugation and block-naturality theorems kernel-checked | Introduce a packet-label map or common labels, an explicit target operator \(T'\), and intertwining hypotheses |
| Dense realization | True under weaker assumptions than stated | Not yet formalized | Continuity plus surjectivity already carries dense sets to dense sets; openness is unnecessary |
| Typed quiver certificate | Algebraic conclusion sound | Not yet formalized | Fix the reachability description and impose finite vertices, or use locally unital path algebras |
| Bilateral shift | Sound over real or complex Hilbert space | Not yet formalized | Replace generic \(k\) by \(\mathbb R\) or \(\mathbb C\); distinguish finite truncation from the infinite proof |
| Elliptic coordinate-ring model | Normal form and multiplication formulas sound | Not yet formalized | Add `char(k) ≠ 2` for the elliptic-curve description; say the parity projectors are \(k\)-linear, not \(A\)-linear |
| Matrix/Jordan computations | Exact symbolic examples agree with the paper | Python regression checked; not Lean theorems | Do not describe two sampled nonzero \(M_4\) seeds as testing every nonzero seed |
| Path and cycle graphs | Claims correct | Endpoint path cyclicity and determinant one are kernel-checked for every nonempty finite path; the cycle formula remains open | Replace the finite-range path computation by the all-\(n\) theorem; say the cycle's *maximum* eigenspace multiplicity is two |

## Corrections required in the manuscript

### Mathematical and typing corrections

1. **Tensor-product proof.** It is false that every simple tensor has the form \((A x_i)\otimes(B y_j)\) for one fixed pair \((i,j)\). Write
   \[
   x=\sum_i A_i x_i,\qquad y=\sum_j B_j y_j,
   \]
   and distribute to obtain
   \[
   x\otimes y=\sum_{i,j}(A_i\otimes B_j)(x_i\otimes y_j).
   \]

2. **Seed-rank conventions.** Define `srank(0)=0`. For modules that need not be finitely generated, use a cardinal-valued minimal generator number (or an explicitly extended natural number); a natural-valued minimum is insufficient without a finite-generation hypothesis.

3. **Single-operator edge case.** Either assume \(X\ne0\) or define the maximum over an empty spectrum to be zero.

4. **Naturality typing.** If source and target packet labels differ, provide a label map \(f:I\to J\). Do not write \(\varphi(T)\) unless \(T\) belongs to the domain algebra. Instead provide \(T'\) and require \(\Phi T=T'\Phi\). A mere vector-space isomorphism does not preserve generator rank for the full target algebra unless the algebra map is onto; otherwise state the result over the image algebra.

5. **Quiver finiteness.** A one-space direct sum and a unital path algebra with \(1=\sum_v e_v\) require finitely many vertices. For infinite quivers, switch to direct sums and locally unital algebra/module language.

6. **Topology.** Add Hausdorffness, completeness, and continuity wherever completion, closed packet ranges, continuous inverse maps, or closed reachability hulls are invoked.

7. **Full block algebra.** Keep the current algebraic statement, or replace arbitrary block homomorphisms by bounded/continuous block maps in a topological setting.

### Example corrections

8. **Typed quiver.** The whole vertex space \(V\) is reachable through \(A\). The missing component is \(\ker B=k e_3\) *inside* that reachable packet. Replace “every path ending in \(V\) factors through \(A\)” with “every path from \(U\) to \(V\) has \(A\) as its final arrow,” since the trivial path at \(V\) is an exception.

9. **Elliptic model.** Write \(M_y^2=M_x^3-M_x\), or the equivalent explicit block-diagonal identity. The projectors \(P_0,P_1\) are \(k\)-linear coordinate projectors.

10. **Cycle graph.** Say that the maximum eigenspace multiplicity is two; exceptional eigenvalues can have one-dimensional packets.

11. **Computation claims.** The code checks finite instances and floating residuals. Universal claims such as “every nonzero \(M_4\) seed is cyclic” come from proof, not exhaustive numerical testing over \(\mathbb C\).

### Publication corrections

12. Add in-text citations and a local bibliography, including sources for minimal module generators, semisimple module structure, cyclic operators/Jordan theory, quiver/path algebras, and block operator matrices.

13. Add a theorem-status table with labels such as `proved here`, `classical/reformulated`, `computed instance`, `conjectural`, and `roadmap`.

14. Shorten the Langlands, quantum, and other future-program passages in Paper I. Keep this installment focused on the algebraic foundation it actually establishes.

## Lean verification status

The current Lean project builds successfully with Lean 4.34.0-rc2 and its pinned Mathlib graph:

```text
Build completed successfully (8878 jobs).
```

The kernel audit reports no project-specific axiom and no `sorryAx`. The only reported dependencies are standard Lean/Mathlib foundations (`propext`, `Classical.choice`, and `Quot.sound`, as applicable).

New Paper I formalizations in this audit are:

- `SeedRankBasics.lean`: defines cardinal-valued seed rank, proves the zero-module and finite cyclicity characterizations, constructs one- and multi-seed quotient presentations, and proves quotient monotonicity and linear-equivalence invariance.
- `PaperITransport.lean`: transports finite projector families through a linear equivalence, proves exact conjugation of transfer blocks, and states a type-correct naturality theorem with explicit source/target operators and intertwining conditions.
- `PaperIBlockCompletion.lean`: upgrades pointwise transfer identities to linear-map equalities and proves the ordinary-matrix support/reflexivity and multiplication-closure/transitivity converses over a nontrivial semiring.
- `SemisimpleSeedRank.lean`: proves that \(r\) matrices generate the one-simple-block module \((k^d)^m\) under diagonal left \(M_d(k)\)-action exactly when \(m\le rd\), and proves that \(\lceil m/d\rceil\) is the least generator count for \(d>0\).
- `FullMatrixCyclicity.lean`: proves constructively that every nonzero finite coordinate vector is cyclic under the full matrix algebra.
- `PathGraphKrylov.lean`: proves for every nonempty finite path, over any commutative ring, that the endpoint walk matrix is unit upper-triangular with determinant one, its finite Krylov family spans, and the endpoint is cyclic.

Already checked results include exact packet-coordinate inverse laws, fibre and residue refinement, transfer-block reconstruction and composition, a concrete four-coordinate rational model, and transitive support closure.

Still outside the checked tranche are the finite-product assembly of the full semisimple maximum formula, the single-operator/Jordan formula, continuous completion and dense realization, adjoints, the cycle-graph formula, the bilateral shift, and the elliptic-coordinate example.

## Disposition

| Dimension | Status |
|---|---|
| Central algebraic correctness | **Pass, subject to the listed repairs** |
| Internal computational consistency | **Pass** |
| PDF/layout integrity | **Pass** |
| Lean coverage | **Substantial finite algebraic tranche; incomplete overall** |
| Standalone citation standard | **Fail pending revision** |
| Archival reproducibility | **Partial** |
| Historical novelty/priority | **Not established** |
| External-publication readiness | **Revise before release** |

The next controlled action should be a revision pass that changes only the fourteen items above, followed by a redline comparison and a second theorem/Lean audit. Paper II should not inherit Paper I's ambiguous conventions or naturality typing.
