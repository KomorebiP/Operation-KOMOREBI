# Independent expanded-manuscript review for the Paper III release

## Primary verdict and exact scope

**Primary verdict: proved as written, for the 59 non-standard result environments in Sections 18–27 of the selected assembled manuscript, with its existing local corrections.** No further substantive mathematical repair was identified in this pass. This is an ordinary mathematical review. It does not establish an expanded Lean correspondence, novelty, or a journal acceptance judgment.

The finite filtered-complex spectral sequence is an external standard fact verified in the exact needed generality against a primary mathematical reference. The other marked standard fact, the projected-connection curvature identity, also has a correct direct proof in the manuscript. Thus the later scope contains **59 result environments, two marked standard facts, and 25 definitions, examples, and remarks: 86 numbered environments altogether.** All 59 results, both facts, all 25 other environments, their setup, the later conclusion, and the added interpretive text in the assembled chapters were read. The sixty accompanying proof environments were read; the finite spectral-sequence fact is supplied by its classical source.

The main reading was the complete raw tail of `source/expanded.tex`, lines 496–2372. That older source is preserved provenance, not the final mathematical statement of every result. I then read the complete line-by-line diff between that tail and the concatenated selected chapters `03_nonlinear_coordinates.tex` and `04_correction_transport.tex`. This verifies unchanged proof bodies against text already read and exposes every selected amendment and added explanation. I also read the standing conventions, relevant earlier packet definitions, bibliography, and the selected master-file inclusion structure.

Section 17 and the separate Section 17 supplement were outside the assigned review. Earlier packet definitions were consulted only as dependencies. I did not review the entire finite manuscript, replay Lean, or rerun the broad computational suites in this mathematical pass.

## Findings that were checked and resolved in the selected manuscript

Two historical-source defects were independently encountered while reading the raw arguments: completeness alone does not permit projecting an infinite convergent series, and derivative invertibility does not produce a zero graph through a base point where the hidden equation is nonzero. Both are already repaired in the assembled chapters. These are not outstanding release defects.

The following existing restrictions and proof repairs were checked directly, rather than accepted from prior audit status:

| Topic | Correct selected contract and why it suffices |
|---|---|
| Infinite packet decoration of trees, 18.3–18.4 | Each underlying tree's finite packet sum stays grouped. An absolutely convergent unlabelled series need not remain absolutely convergent after arbitrary oblique decorations are flattened. The selected text makes only the grouped assertion, and deleting zero decorations preserves each finite group. |
| Convergent higher-operation series, 19.5 | Packet projectors are explicitly continuous in the convergence topology. Finite grading expansions hold at each arity, and continuity then gives the required passage to the convergent sum. Completeness by itself is not the limiting argument. |
| Right-inverse correction, 22.2–22.3 | The right inverse is explicitly bounded and linear. Hence its range is a closed linear correction slice, and the contraction proof uses a genuine operator norm. Uniqueness remains confined to the stated ball in that slice. |
| Filtration finiteness, Section 23 | The selected prose says finite length for the cokernel when the target graded piece has finite length. It does not infer finite cardinality from finite length. The finite branching count separately assumes finite vector spaces over a finite field. |
| Unique lift branch, 23.7 | The correction set is called a coset of the kernel over general modules; the argument does not require the coefficient object to be a field. |
| Exact elimination, 25.1–25.4 | The selected setup declares Banach input and output spaces, an open domain, `F_Q(u_0,v_0)=0`, and a bounded linear isomorphism for the hidden derivative. It also fixes `phi(u_0)=v_0`. These are exactly what the implicit function argument and the displayed base-point derivatives require. |
| Representation of graph holonomy, 26.8 | The based-loop multiplication convention is explicitly the one matching rightmost-first operator composition. Loop products therefore give homomorphisms with the stated variance. |
| Infinite-dimensional unitarity, 27.2 | The selected proof first constructs a two-sided evolution inverse using the bounded operator ODE, then obtains unitarity from `U* U=I`. It does not confuse an isometry with a surjective unitary operator. |
| Degenerate projector data, Section 27 | Self-adjoint bounded idempotence, zero projections, an empty-family maximum convention, the interval, and the empty partition product for `T=0` are declared. The formulas respect these cases. |
| Closed-path convergence, 27.9 | The corollary explicitly assumes a twice continuously differentiable operator-norm packet path. This supplies both the direct-rotation theorem's hypothesis and a Lipschitz generator on the compact interval. |

No new proof was inserted and no existing manuscript, checkpoint, script, or release status was edited by this pass.

## Dependency and obligation review

The proof architecture is acyclic. Some results refer forward for organization—for example the lift-tree theorem uses complete filtered lifting—but complete filtered lifting itself uses only completeness, continuity, separatedness, and compatible approximations, so this is not a logical cycle.

| Unit | Main logical obligations checked | Result |
|---|---|---|
| 18: rooted trees | Multilinear telescoping gives the Lipschitz constant; the scalar majorant preserves the ball; height-bounded trees exhaust all finite allowed trees; their scalar weights increase and remain bounded. The zero source and zero bilinear-map cases and the small Catalan root are consistent. Finite packet reconstruction and grouped zero-term pruning are exact. | Passed |
| 19: graded operations | Labels add under multilinear maps; finite packet expansions are exact; degree-one Lie brackets have the required symmetry in the Maurer–Cartan expansion; `1/2` and factorial invertibility are stated where used; divided-square polarization counts each unordered cross term once; the infinite series uses continuous projectors. | Passed |
| 20: refinement defects | The composition identity comes from adding and subtracting the same intermediate value. The orbit recurrence has zero initial discrepancy. Contraction estimates use `q<1`; multilevel estimates telescope with the correct preceding coarsening norm. Higher derivatives of linear coarsening maps vanish. The affine example attains the stated constant. | Passed |
| 21: obstruction objects | Cokernel solvability and its universal property use the actual correction image. Naturality is a commuting-square quotient construction. Packet splitting requires invariant image or a packet-preserving correction map as stated. Every location of the relative exact sequence is justified by the element chase. The mapping-cone sign gives square-zero differential, and the obstruction criterion has the correct cohomological degree. | Passed |
| 22: analytic correction | Closed range supplies an orthogonal decomposition and bounded pseudoinverse. The least-norm solution is the one perpendicular to the kernel. The selected correction slice is closed. The contraction map preserves the ball, and equation-solutions in the slice are exactly its fixed points. Closed complements and an invertible restricted derivative justify local Lyapunov–Schmidt reduction. Its first and second derivatives remove precisely the terms claimed. | Passed |
| 23: filtered lifting | Congruence preservation makes vertices independent of representatives. The induced linear map on the associated graded is well defined. Lift classes form a kernel coset. Finite branching plus nonempty arbitrarily deep levels gives a compatible branch. The approximations are Cauchy; filtration submodules are closed; continuity and separatedness force the limiting residual to be zero. For Maurer–Cartan lifting, `2m >= m+1` is used only with `m>=1`. No cohomological cocycle claim beyond the stated cokernel is silently added. | Passed |
| 24: filtered complexes | The filtration is finite, exhaustive, and by subcomplexes. The `E_0`, `E_1`, total-degree, and differential conventions match the primary reference. Convergence targets associated graded cohomology; no canonical splitting or solution of an extension problem is claimed. Under degeneration, finite filtered cohomology vanishes exactly when all graded pieces do. In the example `d_1[x]=[y]`, so the total complex is acyclic. | Passed; external construction verified |
| 25: elimination | The corrected zero base point and Banach isomorphism hypotheses give the local hidden graph. Differentiating the hidden equation once gives `Dphi=-A^{-1}D_u F_Q`. Differentiating twice gives the displayed second derivative. Substitution into the retained equation gives both Schur formulas, including all mixed and hidden feedback terms. | Passed |
| 26: finite holonomy | Gauge factors cancel in the stated operator order. Tree propagation produces the unique normalization with fixed root value. Each non-tree edge equation is equivalent to its fundamental-loop condition. Prescribed root intertwiners determine all vertex intertwiners. Restricting both transports and gauges to the structure group gives simultaneous conjugacy classes. Abelian cohomology and projective versions use exactly the same graph/group argument. | Passed |
| 27: smooth transport | Differentiated annihilation gives the packet commutator, and differentiated completeness gives skew-adjointness. The evolution inverse validates conjugation. Both `S* S` and `S S*` are bounded below in the direct-rotation proof, ensuring surjectivity as well as injectivity. Uniform Taylor expansion and the inverse-square-root functional calculus give a quadratic local error. Unitarity prevents norm amplification in the product telescoping bound. The sampled-exponential proof has the same quadratic local and first-order global error. Endpoint packet preservation gives the closed-path restrictions. | Passed |

For the curvature fact, direct calculation on a section `Ps=s` gives `P d(P ds)=P(dP) wedge ds`; substituting `ds=(dP)s+P ds` and using `P(dP)P=0` gives precisely `P(dP wedge dP)P`. This check uses the manuscript's actual connection, not a different geometric surrogate.

## External leaf checked

The manuscript's finite spectral-sequence input was checked against **The Stacks Project, Homological Algebra, Section 12.24**, current official web text consulted on **2026-10-20**:

- [Section 12.24, tag 012K](https://stacks.math.columbia.edu/tag/012K): Lemma 12.24.2 supplies the initial pages and bidegrees; Lemma 12.24.4 supplies functoriality.
- [Lemma 12.24.11, tag 012W](https://stacks.math.columbia.edu/tag/012W): finite filtrations on the complex terms give finite induced cohomology filtrations and convergence.

The manuscript uses a common finite filtration length, a special case of that source. Its `C`, `F`, `p`, `q`, and total degree `p+q` match the reference's `K`, `F`, `p`, `q`, and `p+q`. The implication is **verified**. The source was read through its official HTML; no retained source-file hash or exact Weibel/McCleary page authentication is claimed. This was a bounded theorem check, not a novelty search. The other classical analytic tools were checked at the hypothesis-and-application level in their explicit manuscript arguments; their bibliographic editions were not independently authenticated.

## Formal-source inventory and limits

Within the extracted release tree, excluding the `.lake` vendor dependency tree, the read-only source inventory found **123 `.lean` files with 41 distinct content hashes** at the time of this pass. Those include repeated release/checkpoint copies, historical development snapshots, audit files, negative controls, the accepted finite/Section 16 source, and the two known Section 17 candidates. Repeated files are not separate theorem coverage.

The two expansion candidates are `checkpoint_v0.3.0/formal/drafts/MultilinearPacketJets.lean` and `BoundedPacketJetNorm.lean`. Their headers expressly identify them as uncompiled Section 17 candidates outside the accepted continuation import. I inspected those files and the owned production import/declaration inventory. There is **no recovered Section 18–27 expanded Lean source module in this extracted tree**, and nothing here establishes the claimed 2,693-declaration expanded replay. Vendor mathlib source and old audit/control snapshots do not provide such a manuscript correspondence. No Library search, new source retrieval, or compiler run was performed by this pass.

The statement register correctly treats the 59 later result environments as ordinary mathematical arguments without an accepted expanded Lean map. Its statement hashes refer to the preserved branch source. For exact mathematical closeout, the assembled chapter hypotheses and the existing editorial amendments must continue to travel with those original-source identities; one must not silently replace the corrected selected text with `source/expanded.tex`.

## Provenance and release implication

This was a fresh subagent review of the supplied raw mathematics, followed by a complete comparison with the selected assembled text. The parent supplied task scope and paths, not suspected theorem defects. Prior audit prose and the existing repair ledger were consulted only after the first reading of the mathematical tail. Accordingly, the raw correctness reading was independent of prior findings; the subsequent repair confirmation was an informed reconciliation. Shared model architecture is not mathematical independence evidence by itself.

The later ordinary-mathematics layer supports a scoped final mathematical release with these hypotheses. It supplies no reason to demote correctly stated classical constructions merely because they are expressed in packet coordinates. It also supplies no basis to promote all later statements to fully Lean-formalized status. No additional mathematical gap remains from this assigned scope. Public publication, licensing, full formal replay, and the unassigned sections remain matters for the coordinator's separate release decision.

## Exact revisions

- `checkpoint_v0.3.0/baseline/editable/traditional/source/expanded.tex`: `84affcc82641bcd2b045bcd77b1c11205ee46fd7405b5dce5681b92f0b2ab6ab`
- `checkpoint_v0.3.0/baseline/editable/traditional/chapters/03_nonlinear_coordinates.tex`: `8be2ba36b891f9d86a99b0dc5ab4cde92a08811619580c1d7dd39c88e8d5d188`
- `checkpoint_v0.3.0/baseline/editable/traditional/chapters/04_correction_transport.tex`: `f8792395a24a59415d1f067395dbf799aba0b1e62e46b3d7dadbfcc6c16a4b0d`
- `checkpoint_v0.3.0/baseline/editable/traditional/Paper_III_Traditional_Final.tex`: `03395fd8aa1fb23b34334cf5cd60eb63c26a81e6f69ae1d9c9d3b4a580d711f5`
- `metadata/MANUSCRIPT_STATEMENT_REGISTER_v1.0.0.json`: `84fd4901891f769a1a9f0a27042b8ce6abe0922840abd2c1cbd274ad2b2ebac8`

## Complete later result coverage

The line locators below refer to the selected chapter files; the structured pass also pins each selected statement and proof by SHA-256.

| Number | Label | Chapter / line | Verdict |
|---|---|---|---|
| 18.1 | `thm:polynomial_tree_expansion` | 03:397 | Passed |
| 18.2 | `cor:quadratic_tree_expansion` | 03:441 | Passed |
| 18.3 | `thm:packet_tree_reconstruction` | 03:473 | Passed |
| 18.4 | `cor:tree_pruning` | 03:491 | Passed |
| 19.2 | `thm:graded_convolution` | 03:537 | Passed |
| 19.3 | `cor:cyclic_product` | 03:551 | Passed |
| 19.4 | `thm:packet_mc` | 03:569 | Passed |
| 19.5 | `prop:packet_l_infinity` | 03:601 | Passed |
| 19.7 | `prop:divided_square_packets` | 03:629 | Passed |
| 20.2 | `thm:defect_composition_identity` | 03:704 | Passed |
| 20.3 | `cor:linear_defect_product` | 03:733 | Passed |
| 20.4 | `thm:iterated_orbit_defect` | 03:746 | Passed |
| 20.5 | `thm:fixed_point_stability` | 03:777 | Passed |
| 20.6 | `cor:multilevel_fixed_points` | 03:807 | Passed |
| 20.7 | `prop:derivative_defects` | 03:829 | Passed |
| 21.2 | `thm:cokernel_obstruction` | 03:873 | Passed |
| 21.3 | `thm:obstruction_naturality` | 03:906 | Passed |
| 21.4 | `thm:packet_obstruction_decomposition` | 03:929 | Passed |
| 21.6 | `prop:obstruction_quotient_projectors` | 03:965 | Passed |
| 21.7 | `thm:relative_obstruction_sequence` | 03:997 | Passed |
| 21.8 | `cor:coarse_fine_obstruction` | 03:1052 | Passed |
| 21.11 | `thm:cone_obstruction` | 03:1089 | Passed |
| 21.12 | `cor:packet_obstruction_complexes` | 03:1118 | Passed |
| 22.1 | `thm:orthogonal_obstruction` | 04:5 | Passed |
| 22.2 | `thm:right_inverse_correction` | 04:36 | Passed |
| 22.3 | `cor:correction_stability` | 04:94 | Passed |
| 22.4 | `thm:lyapunov_schmidt` | 04:114 | Passed |
| 22.5 | `cor:quadratic_reduced_obstruction` | 04:163 | Passed |
| 23.2 | `thm:one_step_lifting` | 04:250 | Passed |
| 23.3 | `cor:finite_branch_count` | 04:275 | Passed |
| 23.4 | `lem:well_defined_lift_classes` | 04:288 | Passed |
| 23.6 | `thm:finitely_branching_lift_tree` | 04:312 | Passed |
| 23.7 | `cor:unique_lift_branch` | 04:326 | Passed |
| 23.8 | `thm:complete_filtered_lifting` | 04:334 | Passed |
| 23.9 | `thm:filtered_obstruction_naturality` | 04:363 | Passed |
| 23.11 | `prop:maurer_cartan_lifting` | 04:384 | Passed |
| 24.1 | `fact:filtered_spectral_sequence` | 04:429 | External fact verified |
| 24.2 | `prop:fine_obstruction_survival` | 04:449 | Passed |
| 24.3 | `cor:direct_packet_no_cancellation` | 04:457 | Passed |
| 25.1 | `thm:exact_local_elimination` | 04:520 | Passed |
| 25.2 | `thm:schur_derivative` | 04:538 | Passed |
| 25.3 | `thm:schur_second_derivative` | 04:570 | Passed |
| 25.4 | `cor:reduced_packet_jets` | 04:604 | Passed |
| 26.2 | `prop:gauge_covariance` | 04:658 | Passed |
| 26.3 | `thm:tree_normalization` | 04:672 | Passed |
| 26.4 | `thm:cycle_gluing` | 04:680 | Passed |
| 26.5 | `cor:cycle_number` | 04:688 | Passed |
| 26.6 | `thm:holonomy_intertwining` | 04:708 | Passed |
| 26.7 | `cor:scalar_holonomy_bridge` | 04:735 | Passed |
| 26.8 | `thm:gauge_classification` | 04:743 | Passed |
| 26.9 | `cor:abelian_holonomy_class` | 04:759 | Passed |
| 26.10 | `cor:projective_transport` | 04:773 | Passed |
| 27.1 | `lem:packet_commutator` | 04:808 | Passed |
| 27.2 | `thm:kato_transport` | 04:848 | Passed |
| 27.3 | `cor:one_moving_subspace` | 04:879 | Passed |
| 27.5 | `prop:packet_direct_rotation` | 04:906 | Passed |
| 27.6 | `lem:one_step_direct_rotation` | 04:948 | Passed |
| 27.7 | `thm:direct_rotation_convergence` | 04:996 | Passed |
| 27.8 | `thm:sampled_transport_convergence` | 04:1055 | Passed |
| 27.9 | `cor:continuous_holonomy` | 04:1089 | Passed |
| 27.11 | `fact:projected_curvature` | 04:1114 | Passed |
