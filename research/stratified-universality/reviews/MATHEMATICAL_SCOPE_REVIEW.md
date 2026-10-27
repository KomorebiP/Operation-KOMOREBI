# Stratified Universality: bounded mathematical release review

Date: 2026-10-06. Reviewer: a separate subagent reading the raw v2.0.0 sources. This is a bounded release review, not a referee audit of every native-stratum proof in the 247-page manuscript. The proof-audit skill was used. No manuscript source was edited by this reviewer and no research ledger was initialized.

**Primary verdict: correct only after the stated local restrictions and corrections below.** The finite lane, twisted transport, behavioral quotient, module semantic diamond, carrier factorization, bridge loss, admissibility monotonicity, and forgetful-lifting cores reviewed here have coherent written arguments under their explicit hypotheses. The original release overstates nonzero selector action, omits finite aggregation hypotheses in the observer-packet layer, and uses a sequential-compactness implication not available from compact Hausdorffness alone. These corrections do not establish unrestricted universality or new cross-doctrine existence theorems.

## What was actually reviewed

Source root:

`/workspace/scratch/cbc2b5a746c7/work/stratified/upstream/Komorebi_Stratified_Universality_Formal_Foundations_v2.0.0_Source/manuscript`

- `block15_section.tex`: definitions of finite profiled lane systems; theorem `thm:block15-universal-lane-transport`, L1–L8 and its proof; finite atlas descent `thm:block15-lane-descent`, proof, corollary, and boundary.
- `block16_section.tex`: holonomy-profiled data, matrix local systems; theorem `thm:block16-holonomy-twisted-lane-transport`, H1–H5 and its proof; base-fiber invariant normal form; orbit descent O1–O5 and its proof; permutation-module orbital theorem statement and beginning of proof.
- `block17_semantic_quotients.tex`: the complete semantic-slice, behavioral quotient, core/coinduction, task Galois, quotient lattice, semantic diamond, relative residual, and task-loss chain.
- `block18_carrier_observer_change.tex`: carrier factorization and joint completion, task-compatible bridge and loss composition, monoid observer packets, semiring barriers, observer base-change sequence, polyphase Hankel example, convex/provenance statements and proofs.
- `block19_admissibility_lifting.tex`: complete admissibility, compactness, metric, convex-versus-quadratic, unipotent escape, forgetful lifting, and relative synthesis layer.
- The integrated main source's maximal flat core theorem (approximately lines 1464–1510), abstract/introduction scope statements, and finite atlas assembly statement/proof; `publication_scope_section.tex`, `appendix_claim_ledger.tex`, `RELEASE_NOTES_v2.0.0.md`.
- `Komorebi_Theorem_Concordance_v0.4.json`: summary, controlling sources, all conditional/conjectural rows, and relevant FND-16/FND-17, SEM, CAR, BRG, CVX, ADM, DOC rows.
- `verify_block17_semantic_extension.py`: inspected the actual computation and source-contract assertions. Its verifier was not rerun by this reviewer; fresh replay belongs to the release verification task.

Native-stratum results such as general regular-sequence normalization, Smith–Fitting lattices, holonomic irreducibility, algebraic packet degrees, nonlinear trees, Galois/Brauer/Tannakian descent, and the five-component classification were **not independently re-audited in full**. Named external mathematical sources were not authenticated afresh in this bounded review; their exact-source leaves remain outside this review, rather than being certified by reading a bibliography or concordance.

## Normalized claim cards and obligation matrix

| Claim | Exact scope and critical dependencies | Review result |
|---|---|---|
| Finite lane transport | Additive idempotent-complete category; finite, complete, pairwise annihilating idempotents with chosen splittings; coherent projector-sum refinement. L1–L6 follow by finite biproduct reconstruction and distributivity. Realization and folds have separate preservation/injectivity/retraction hypotheses. | Passed for the core reviewed. Empty address sets force the ambient object to be zero; no dimension/compression conclusion follows from lane count. |
| Ordinary atlas lane descent | Actual descent objects/morphisms, additive transitions, coherent address bijections and splitting comparisons, plus a global address trivialization. Chartwise kernels additionally require kernel preservation and coherent comparisons. | Passed under the stated hypotheses. The theorem constructs no absent passport and does not supply unrestricted effectivity. |
| Twisted lane transport | Finite connected chart groupoid; additive equivalences; complete split lanes; address/splitting cocycles and refinement equivariance. Analysis and synthesis restrict to compatible families; composition transports by conjugation and reindexing. | Passed for H1–H5. Equivariant selectors, not arbitrary local support choices, act on the section group. |
| Monodromy orbit descent | Coherent finite address action; globally labeled coarsening is explicitly constrained to equivariant sums of original lanes. | O1–O3 and O5 passed. O4's support classification passes; its unqualified nonzero-operator phrase fails as explained below. |
| Maximal flat core | Finite connected graph, finite-dimensional vector spaces, invertible edge transports with reverse edges inverse. Root evaluation identifies sections with common fixed space of fundamental holonomies. | Passed for the direct internal argument. Global sections do not imply a global frame on full fibers. |
| Behavioral coimage/core | Fixed continuation action and observations in Set/a variety or modules; relevant effective quotient exists. Kernel pair inclusion gives the factor map; identity continuation and word closure give maximality. | Passed. Quotient is relative to the semantic slice. Effective computation for arbitrary infinite input languages is not implied. |
| Coinduction/finite stabilization | Generator family; behavioral kernel is a fixed point; every fixed point is invisible and generator-stable. Finite states or finite-dimensional modules bound strict refinements/dimension drops. | Conclusion passed; proof contains a minor overly strong characterization sentence, noted below. Effective certification still requires an accessible finite presentation of the constraints. |
| Semantic diamond/residual | Two surjective module maps, kernels N and M; exact sequence uses difference of quotient coordinates and lifts compatible pairs via a-b=n+m. | Passed. Pullback identity is module-relative; canonical splitting is expressly not claimed. |
| Carrier/joint completion | Homomorphisms from one raw algebra with one fixed operation signature; effective image factorization. Fiber inclusion makes the factor map well-defined. | Passed. It neither identifies incompatible carrier laws nor makes arbitrary bridges equivalences. |
| Bridge loss/composition | Linear bridge satisfying f(N_X)⊆N_Y; simplified composition requires induced surjectivity. | Passed. Loss is extension data and does not canonically split. |
| Observer packets/convex transport | Commutative monoid aggregation requires finite branch fibers and finite raw-history aggregation; convex max formula requires finite branches and a convention for empty fibers. | Correct only after the explicit finite/empty conventions below. |
| Admissibility/escape | Infimum over a larger class weakens defect; escape requires zero infimum not attained and compact conditioned sublevels with continuous defect. | Monotonicity passed. Escape statement survives, but the compactness proof needs the replacement below. |
| Metric examples/lifting | Positive-definite metrics; invertible maps; normalized graph holonomy. Sharp 2×2 norm identity and unipotent calculation are internal. Forgetful composition gives only an underlying bridge; enhancement requires extra data. | Exact examples and lifting scope passed. Compact-group averaging is an external classical leaf not authenticated afresh here. |

The dependency graph is local and explicit: complete split idempotents → analysis/synthesis → matrices and selectors → coherent transition restriction → twisted sections and orbit support; future observations → kernel intersection → quotient/core → module exact sequences; common raw algebra → fiber criterion → carrier factorization/joint image; continuous nonnegative defect + compact conditioned sublevel → attained positive lower bound on that sublevel → eventual escape. No circular dependency was found in these reviewed chains.

## Required release amendments

### 1. Pair-orbit support atoms versus nonzero selector action

Location: `block16_section.tex`, theorem `thm:block16-orbit-descent`, (O4), and the corresponding supported claim in `appendix_claim_ledger.tex`.

Replace the final O4 sentence by:

> The minimal nonempty compatible supports are therefore the single pair orbits. Their associated selectors need not act nontrivially on the section group: a single-orbit selector is nonzero exactly when that orbit supports a nonzero compatible section.

Add to its proof that the selector acts as identity on orbit-supported sections and annihilates complementary support. The union-of-orbits classification remains unchanged.

**Decisive counterexample to the original nonzero phrase:** take the one-chart groupoid with loop group C₂, chart category Q-Vect and identity transition functors. Give X=Q trivial descent action and Y=Q sign action. Each has one lane and its address is fixed. The base pair-address set has one nonempty orbit. Compatible maps h:X→Y satisfy -h=h, so h=0 over Q. Thus the only single-orbit selector is the zero endomorphism of the zero section group. All H1–H5 assumptions hold. A nonempty address orbit does not guarantee nonzero invariant morphisms.

The appendix's “minimal nonzero holonomy-compatible Boolean transport selectors” should become “minimal nonempty holonomy-compatible Boolean transport supports; their selectors are nonzero only on orbits supporting nonzero compatible sections.” FND-17 should retain its core status with an explicit release-amendment note and corrected source hash. Do not describe the original O4 wording as proved as written.

### 2. Finite aggregation and empty observer fibers

Location: `block18_carrier_observer_change.tex`, theorem `thm:block18-carrier-indexed-observer` and the convex packet subsection/theorem.

Make B a **finite branch alphabet**. State that the raw histories being aggregated form a finite family and that the monoid empty sum is 0. This preserves the intended finite theorem. For example, A=N under addition, one state, B=N, all branch actions identity and one input value 1 would demand an undefined infinite monoid sum in the original statement.

In the convex subsection, specify a finite branch alphabet and compact convex packets allowed to be empty. Use:

- conv(∅)=∅;
- h_∅(x)=-∞;
- max∅=-∞.

The theorem's displayed maximum then remains valid for every target state, including targets with no incoming branch. In the proof, handle the empty fiber first; both sides are -∞. Otherwise the linear-image support identity and the support maximum of a **finite** union prove the formula. Finite-dimensional convex hulls of finite unions of compact sets are compact. The carrier of compact convex packets includes ∅ as the aggregation identity; nonempty convex bodies alone do not form this monoid.

CAR-02's hypotheses need finite branching, finite raw-history aggregation, and the empty-sum convention. CVX-01's hypotheses need finite branches and the empty-packet convention. The existing full-dimensionality/invertible-continuation premises for the separate hiding result must remain intact.

### 3. Compactness proof preserving eventual violation of every bound

Location: `block19_admissibility_lifting.tex`, proposition `prop:block19-escape-compactness`.

The original statement is supportable, but its proof takes a convergent subsequence from compact Hausdorffness, which is not generally valid, and only discusses a uniformly conditioned full sequence. Replace the proof by:

> Fix a declared conditioning bound c, write Γ_c for the parameters satisfying it, and let K_c={g∈Γ_c : d(X,g)≤1}. By hypothesis K_c is compact. If K_c is empty, every near-minimizing sequence eventually has defect below 1 and therefore lies outside Γ_c. Otherwise continuity gives an attained minimum a_c=min_{g∈K_c}d(X,g). Since the zero infimum is not attained anywhere in Γ, a_c>0. Every near-minimizing sequence eventually has defect below min{1,a_c}, and therefore cannot belong to Γ_c. Since c was arbitrary, each fixed conditioning bound is eventually violated; in particular no subsequence satisfying one fixed bound can be near-minimizing.

This argument uses the stated conditioned-sublevel compactness and continuity directly. It does not add metrizability or sequential compactness. ADM-01 should record a proof correction with no change to its conclusion.

## Additional local clarifications

- In `thm:block17-coinductive-characterization`, “A fixed point is precisely an invisible congruence or submodule stable under every generator” is stronger than needed and false in the reverse direction. Any fixed point is invisible and stable, while the greatest invisible stable core is a fixed point. For instance, with only identity continuation, Φ(R)=K₀ for every R, yet proper R⊂K₀ can also be invisible and stable. Replace that sentence by the two correct implications. The greatest-fixed-point theorem remains correct: if x∈Φ(N_S), its identity observation vanishes and each first-generator successor has all future observations vanish, so every continuation word is invisible; hence Φ(N_S)=N_S.
- The adjacent finite-certification proof should explicitly identify the stabilized fixed point with the **greatest** fixed point: the behavioral core lies in the initial N₀ and monotonicity of Φ preserves its containment at every stage. Thus the stabilized fixed point contains the behavioral core; greatest-fixed-point maximality supplies the reverse inclusion. This is a proof clarification with no statement change.
- Define determinant-normalized holonomy concretely as H↦|det H|^{-1/n}H for positive dimension n. This avoids complex-root choices; metric distortion formulas need positive-dimensional spaces or a separate zero-dimensional convention.
- The metric criterion's sufficiency argument is clearest without an unqualified path-independence claim for unnormalized metric transport. Choose tree maps G_v and set Q_v=(G_v⁻¹)*Q_oG_v⁻¹. For an edge e:u→v, write H_e=G_v⁻¹T_eG_u. Invariance under the normalized H_e implies H_e*Q_oH_e=|det H_e|^{2/n}Q_o, hence the required edge relation with λ_e=|det H_e|^{1/n}. Conversely a compatible family makes root holonomies conformal; determinants fix the scale, so normalized holonomy preserves Q_o. This proves the internal equivalence directly while leaving compact-closure averaging as the classical external leaf. Reverse graph traversal must use inverse transports.
- The manuscript README still describes the v1.16.0 build while v2.0.0 release notes use Build_v2.sh. This is documentation drift, not a mathematical counterexample.

## Evidence boundaries and provenance

The concordance actually has 75 component rows: 52 “proved internally,” 12 classical imported/reinterpreted, 2 conditional, 3 framework, 6 conjectural. Component rows are not individual theorem counts and do not give a completion percentage. Conditional atlas effectivity and conjectural unrestricted assembly remain explicit. A publication-integrity PASS does not turn those rows into established unconditional results.

The Part IV validator checks 1,000 seeded integer-matrix trials for dimensions and a factorization condition, one exact symbolic quadratic identity, Hankel determinants at N=1…8, and source-label contracts. Its 3,022 assertions are exact bounded implementation evidence, not proofs of all universal statements. In particular, its source-contract checks only test labels/literal placeholders and cannot detect the three logical issues above.

No .lean module, Lake project, or Lean toolchain was present in the reviewed manuscript source tree. The release notes explicitly say Part IV was not formalized in Lean. This review neither erases Lean proofs of antecedents elsewhere nor certifies whole-manuscript Lean correspondence. The Lean companion must identify exact available antecedent declarations and expose unmapped manuscript results honestly.

Read source hashes:

| File | SHA-256 |
|---|---|
| `block15_section.tex` | `c1ae8aa2472eda9df467bbbf20b3c861f1261333364af06ffaf1cd455b5ab026` |
| `block16_section.tex` | `2f4d6deaa95f51b17f4ba107c2b202f28e3b58cca6da516ca3233ed8dd3747ba` |
| `block17_semantic_quotients.tex` | `d8355db51d374b93114e9f2f00de7f6bf529eee89939573e3da51fecea981bc6` |
| `block18_carrier_observer_change.tex` | `9307836727c1bfdb7159d883529812c920dd9517c6042a72383876e45aaebbd0` |
| `block19_admissibility_lifting.tex` | `9368eeae300343c809895304e35c454514b32b4369e03354ad00317b6da5f1dc` |
| `Komorebi_Theorem_Concordance_v0.4.json` | `78ccefc5ec4beca81c20e644f3c7138923492cf5d9a1aa30f639bb35fccf1d79` |

Strongest safe release statement: the amended, explicitly finite and profiled transport/quotient/carrier calculus is supported by the written proofs reviewed here, with named external and unrestricted-atlas obligations retained. The cheapest next check is to inspect the final-use amended source copies, confirm that the appendix and concordance use the same corrected scope, then replay the exact validators and compile/render the release. No claim is made that those checks substitute for a full independent audit of all native strata.

## Final-use amendment review

The separate final-use `block16_section_final.tex`, `block18_carrier_observer_change_final.tex`, `block19_admissibility_lifting_final.tex`, and `appendix_claim_ledger_final.tex` under the 2026-10-06 traditional release directory were compared against their inherited originals. The three required amendments above and their supporting proofs passed this bounded review. The amended FND-17, CAR-02, CVX-01 and ADM-01 rows in `Komorebi_Theorem_Concordance_Final_2026-10-06.json` retained the 75 component IDs/statuses while explicitly recording the corrected release scope. This addendum does not claim a new audit of unchanged native-stratum proofs or a fresh validator replay.

The subsequent final-use `block17_semantic_quotients_final.tex` was read at the coinductive theorem and finite-certification proofs. Both correct implications and the monotone containment induction are present and passed review. The further metric conventions and proof in `block19_admissibility_lifting_final.tex` were read: common positive dimension, absolute-determinant normalization, inverse reverse traversal, determinant necessity, and the explicit spanning-tree sufficiency calculation are all coherent over real or complex fibers. The classical compact-closure averaging leaf is retained rather than claimed newly source-authenticated. SEM-03 and the separate supporting-metric record in the final concordance explicitly record these changes. The full finite raw-history premise in the final-use Block 18 theorem was rechecked, alongside finite states, finite branches, and empty aggregation.

**Final-use review outcome:** all five amendment groups passed this bounded review; none changes an unreviewed native-stratum result or supplies an unrestricted assembly/recognition/existence claim. The remaining unreviewed/external leaves listed above retain their prior status and are not promoted by this review.

Final-use files reviewed at these hashes:

| File | SHA-256 |
|---|---|
| `block16_section_final.tex` | `2b086cc6d806c3cf25b443a6ecefa871adba282d913deffaafabcadad2c0258a` |
| `block17_semantic_quotients_final.tex` | `ef408f87352057761b6bf55742f848612f585632691f71488d510393749b0735` |
| `block18_carrier_observer_change_final.tex` | `6babbf13d884e5bdf86174ce89729ccf69feb694cf84e03c0f52c32038775157` |
| `block19_admissibility_lifting_final.tex` | `038f352d1e9a82984963af0e90a14b104b8f17f7b2e8e4df2c8da627bc089799` |
| `appendix_claim_ledger_final.tex` | `4086d789d942d7e813d9b23e92a9692f15b8f2e1bce03a19e3e3d1bb6737d5b7` |
| `Komorebi_Theorem_Concordance_Final_2026-10-06.json` | `ffb2caa42ec3f8905bc55e6508c4163ae55f94c8fe991e44727b200f2a396b9b` |
