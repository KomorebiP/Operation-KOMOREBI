# Independent source audit: profinite residue stabilizer surjectivity

Date: 2026-09-08. Scope: read-only extraction of the pinned Mathlib theorem and audit of its action, invariant-ring, continuity, and reduction-map application to the exact frozen production source. No production sources were modified. The source was initially read provisionally and then reread and pinned after the parent communicated its freeze at passing attempt 3. Independent production compilation is being handled by the parent.

Frozen production source: `/root/.codex/tmp/paperx_block26/lean/PaperX/AbsoluteIntegralFrobenius.lean`, 5728 bytes, SHA256 `5b65258e7664f6905c4164cfeaa35f8af0270fe78696c047601724c16422b8ed`. Its exact bytes are retained as `AbsoluteIntegralFrobenius.frozen.lean` in this private audit directory. Later production changes invalidate this application-source verdict until rechecked.

**Verdict:** the cited external theorem genuinely gives every automorphism of the actual residue extension as reduction of one element of the actual acting group stabilizing the ideal, provided its explicit hypotheses hold. No concrete defect was found in the theorem or in the frozen application's `IsGaloisGroup`, continuity, and reduction-map instance chain. The external theorem supplies the compatible infinite lift, so the application does not need to postulate compatible finite lifts or surjectivity of a decomposition map.

## Authentication and executable check

Repository root:
`/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2/workspace/.lake/packages/mathlib`.

Pinned commit: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Main source: `Mathlib/RingTheory/Invariant/Profinite.lean`, theorem at line 175. SHA256: `238832f299099333b7d63a03db00b03e315c5357ff9fff57d6232406a0cbfdf0`.

Stable locator: https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/RingTheory/Invariant/Profinite.lean

All 17 source files listed with their full paths and SHA256 values in `SourceManifest.json` were compared byte-for-byte with `git show HEAD:<path>` and match the pinned commit. `SourceProbe.lean` was run with the pinned Lean binary and only pinned runtime dependency paths, excluding the project build directory. It exited 0 with no stderr. `SourceProbe.stdout` records fully explicit theorem signatures and axiom sets. The profinite theorem, `IsGaloisGroup.of_isFractionRing`, `IsGaloisGroup.of_isGalois`, and `stabilizer_isOpen_of_isIntegral` each depend only on `propext`, `Classical.choice`, and `Quot.sound`.

Limitation: the probe reads pinned runtime compiled objects; this sub-audit did not rebuild Mathlib. Selected loaded object hashes are recorded separately in the manifest. Source authentication and compiled-object inspection are distinct checks.

## Exact contract and object dictionary

For types `A`, `B`, and `G`, the theorem requires:

| Data or hypothesis | Exact meaning |
| --- | --- |
| `[CommRing A] [CommRing B] [Algebra A B]` | A specified commutative ring extension. |
| `[Group G] [MulSemiringAction G B]` | The specified group acts by ring automorphisms of B. |
| `[SMulCommClass G A B]` | The action commutes with scalar multiplication from A, hence fixes the image of A. |
| `[TopologicalSpace G] [CompactSpace G] [TotallyDisconnectedSpace G] [IsTopologicalGroup G]` | The topology and group operations make G profinite in Mathlib's unbundled hypotheses. |
| `[TopologicalSpace B] [DiscreteTopology B] [ContinuousSMul G B]` | The action on the discrete ring is jointly continuous; equivalently, every element stabilizer is open. |
| `P : Ideal A`, `Q : Ideal B`, `[Q.IsPrime] [Q.LiesOver P]` | Q is prime and its contraction is P. P being prime follows; no independent P-prime or maximality parameter is required. |
| `[Algebra.IsInvariant A B G]` | Every b fixed by every g belongs to the image of A. |

`Algebra.IsInvariant` is defined in `RingTheory/Invariant/Defs.lean:31` by the exact proposition
`∀ b : B, (∀ g : G, g • b = b) → ∃ a : A, algebraMap A B a = b`.

The conclusion is `Function.Surjective (Ideal.Quotient.stabilizerHom Q P G)`.
The map, defined in `RingTheory/Ideal/Over.lean:341`, is the monoid homomorphism

`MulAction.stabilizer G Q →* ((B ⧸ Q) ≃ₐ[A ⧸ P] (B ⧸ Q))`.

For `g` in this stabilizer and `b : B`, it sends the class of b to the class of `g • b` (`stabilizerHom_apply`, line 350). The stabilizer is the subgroup of the actual G whose induced ideal action satisfies `g • Q = Q`. The map is induced by `MulSemiringAction.toAlgEquiv A B g`; it is not an arbitrary homomorphism later labeled reduction.

There is no explicit finite-group, finite-dimensional, residue-finiteness, normality, faithfulness, separability, or `IsGaloisGroup` hypothesis in this theorem. Its target consists of algebra automorphisms of quotient rings. When Q is maximal, B/Q is a field. Inertia is the kernel (`Over.lean:354`), but the theorem's witness already lies in the actual stabilizer, before passing to inertia.

## Proof arrows

Fix an arbitrary target automorphism σ. For each open normal subgroup N of G, put `B_N = FixedPoints.subalgebra A B N` and `Q_N = Q.under B_N`. The quotient group G/N acts on B_N. The inherited invariant property is proved in `Invariant/Basic.lean:78`; it follows from invariance for G, not from a separate assumption at every N.

There is a canonical injective quotient map `f_N : B_N/Q_N →ₐ[A/P] B/Q`. The auxiliary fiber at N consists of elements τ_N of the stabilizer of Q_N in G/N satisfying the exact equality of algebra homomorphisms

`f_N.comp (stabilizerHom Q_N P (G/N) τ_N).toAlgHom = σ.toAlgHom.comp f_N`.

These are the objects of `stabilizerHomSurjectiveAuxFunctor` (`Profinite.lean:129`). An inclusion N ≤ N' gives G/N → G/N' and B_N' ⊆ B_N. The transition function is the quotient group map. Its stabilizer property follows by contracting ideals through the subalgebra inclusion (`Profinite.lean:111`), and the displayed reduction equation restricts to B_N'. Thus the proof constructs all transition maps and proves their coherence.

Each fiber is finite because it is a subtype of G/N, which is finite for open N in compact G (`Profinite.lean:151`). Each fiber is nonempty (`Profinite.lean:157`) by two finite-group theorems:

1. `exists_algEquiv_fixedPoint_quotient_under` (`Invariant/Basic.lean:451`) restricts σ to an automorphism of B_N/Q_N. This uses its embedding in the domain B/Q and invariance under the finite group G/N. The underlying restriction argument uses a finite orbit polynomial with coefficients in A; the same argument applied to σ inverse gives an equivalence.
2. `Ideal.Quotient.stabilizerHom_surjective` (`Invariant/Basic.lean:360`) lifts that restricted automorphism to the stabilizer in G/N. Its proof uses the fraction-field stabilizer theorem (`Basic.lean:351`) and injectivity of extension of quotient-ring automorphisms to fraction fields.

The category of open normal subgroups ordered by inclusion is cofiltered: finite intersections provide common refinements. `nonempty_sections_of_finite_cofiltered_system` produces a coherent family τ_N from the nonempty finite fibers. It does not require surjective transition maps.

Forgetting the fiber conditions leaves a compatible family in all G/N. The inverse of `ProfiniteGrp.isoLimittoFiniteQuotientFunctor` supplies one `a : G`, with its image in every G/N equal to τ_N. The proof then checks both required global properties elementwise:

- For b in B, continuity and discreteness make its stabilizer open; an open normal N inside that stabilizer places b in B_N. The finite stabilizer property at N then proves `a • Q = Q`.
- For the same reason, every representative b of a quotient class lies in some B_N. The defining fiber equation at N proves `stabilizerHom Q P G a [b] = σ [b]`.

Consequently one actual a stabilizes Q and induces σ on every residue class simultaneously.

## Where compactness enters

1. Compactness of G makes each open-subgroup quotient finite, hence makes the lifting fibers finite.
2. Compactness and total disconnectedness give a clopen neighborhood basis. `ProfiniteGrp.exist_openNormalSubgroup_sub_open_nhds_of_one` (`ClopenNhdofOne.lean:48`) then puts an open normal subgroup inside an element stabilizer. Its proof first obtains an open subgroup and then takes its finite-index normal core.
3. `CategoryTheory/CofilteredSystem.lean:66,79` puts discrete topologies on the finite fibers and invokes the compact Hausdorff inverse-limit theorem. `TopCat/Limits/Konig.lean:126` proves nonemptiness by a directed intersection of closed, nonempty partial-section sets inside a compact product. This is the compatibility step.
4. `ProfiniteGrp/Limits.lean:120` proves surjectivity of G → lim G/N because its image is dense and closed; closedness uses compactness of G and Hausdorffness of the limit. Separation gives injectivity, and line 151 packages the inverse used by the residue theorem.

The application also obtains compactness of the absolute Galois group from `FieldTheory/Galois/Profinite.lean:329`, through the independently constructed equivalence with the limit of finite Galois groups.

## Frozen absolute-Galois application

The inspected production definitions use A = ℤ, B = `integralClosure ℤ (AlgebraicClosure ℚ)`, G = `Gal((AlgebraicClosure ℚ)/ℚ)`, and P = `(p)`. This is the actual ring of algebraic integers inside the fixed algebraic closure and the actual absolute Galois group.

The integral-closure action is inherited pointwise from the field action. In `IntegralClosure/Algebra/Basic.lean:264`, `g • x` is the subtype whose underlying field element is `g • (x : K)`, with integrality preserved by the ring automorphism. `integralClosure.coe_smul` at line 274 is `rfl`. The associated `SMulDistribClass` at line 280 makes the ring-to-field action compatible.

The invariant-ring instance is not the finite-extension theorem `Algebra.isInvariant_of_isGalois`. It follows from the genuinely infinite-compatible chain:

- `IsGaloisGroup.of_isGalois` (`FieldTheory/Galois/IsGaloisGroup.lean:77`) gives the field instance, using `InfiniteGalois.mem_bot_iff_fixed` (`Galois/Infinite.lean:110`). That theorem assumes `[IsGalois ℚ Qbar]` with no finite-dimensional assumption. Algebraic closure in characteristic zero supplies the Galois hypothesis.
- `IsFractionRing.comap_isAlgebraic_iff` (`Localization/Integral.lean:122`) makes Qbar algebraic over ℤ, and `integralClosure.isFractionRing_of_algebraic` (line 390) makes Qbar the fraction field of B. The latter uses denominator clearing for each algebraic element, not finite degree of the whole extension.
- `IsGaloisGroup.of_isFractionRing` (`RingTheory/IsGaloisGroup/Basic.lean:85`) applies because ℤ is integrally closed, B is integral over ℤ, both fraction fields and scalar towers are specified, and the actions agree with the embedding. It has no `[Finite G]` hypothesis. For a fixed b in B, its image in Qbar belongs to ℚ by the field invariant property; its integrality then forces it into ℤ. This proves the required invariant condition rather than assuming it.
- `IsGaloisGroup.commutes` and `.isInvariant` are low-priority instances (`Defs.lean:118`), so the stronger ring instance supplies exactly the two algebraic hypotheses used by profinite stabilizer surjectivity. Its additional faithfulness field is harmless and unnecessary for the latter theorem.

The inspected `continuous_integral_action` uses `continuousSMul_iff_stabilizer_isOpen` (`Topology/Algebra/MulAction.lean:287`) and identifies an integral-subtype element stabilizer with its field element stabilizer. `stabilizer_isOpen_of_isIntegral` (`KrullTopology.lean:260`) proves the latter open by the finite extension generated by that single algebraic element. This supplies genuine continuity for the actual action on discrete B.

After these hypotheses and the residue Frobenius algebra-equivalence are proved, the external theorem therefore yields an element in the actual absolute-Galois stabilizer of Q with reduction `[x] ↦ [x]^p`. The frozen source's `exists_frobenius_at` applies it exactly to `residueFrobenius p Q`, obtains the automorphism equality `hσ`, and evaluates that equality on each quotient class. This has the required forward p-power convention. It neither swaps σ with its inverse nor substitutes an unrestricted lift from the full group.

The external theorem does not itself construct the residue Frobenius equivalence, choose a maximal ideal above p, or establish a connection to any separately defined valuation decomposition group or finite-extension restriction. The frozen source proves its own residue perfectness and maximal-ideal existence; the parent is auditing those separate claims. This report certifies the external implication and its exact frozen action/invariant/continuity/reduction-map attachment. It does not certify the still-developing larger block assembly or any unproved valuation identification.
