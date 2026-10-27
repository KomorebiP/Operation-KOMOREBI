# Paper I: complete mapped declaration crosswalk

Each entry resolves in the fresh build and the source-owned inventory. Source line numbers locate declarations. The full elaborated signature, including section parameters and universe information, is retained in the referenced compiler log. These are 73 theorem declarations and 11 definitions/equivalences, not 84 independent theorems.

## Row 1 — Universal one-seed presentation

**Contract scope:** For the module map `a ↦ a • s`, the quotient by its kernel is linearly equivalent to its exact range; the glue theorem verifies that the class of `a` maps to `a • s`; and singleton generation is equivalent to surjectivity. If the induced map from the normed quotient is supplied as a continuous linear isometry with dense range into a Banach target, it extends uniquely to a continuous linear equivalence from the completion and intertwines supplied bounded operators.

**Exclusions:** No norm, isometry, density, or bounded extension is constructed automatically on the algebraic quotient. The annihilator is only the typed left submodule/left-ideal object; no two-sided ideal claim is made.

`Komorebi.SeedRankBasics.oneSeedQuotientEquivRange`  
definition at `source/main/KomorebiVerification/SeedRankBasics.lean:224`. Signature log starts at line 1. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SeedRankBasics.oneSeedQuotientEquivRange_apply_mk`  
theorem at `source/main/KomorebiVerification/SeedRankBasics.lean:236`. Signature log starts at line 7. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SeedRankBasics.generates_singleton_iff_surjective`  
theorem at `source/main/KomorebiVerification/SeedRankBasics.lean:94`. Signature log starts at line 12. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense`  
definition at `source/main/KomorebiVerification/TopologicalCompletion.lean:291`. Signature log starts at line 17. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_intertwines`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:323`. Signature log starts at line 26. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_unique`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:339`. Signature log starts at line 49. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 2 — Multi-seed presentation

**Contract scope:** An arbitrary Finsupp-indexed family has the free-module quotient presentation; the glue theorem verifies that a coefficient family maps to its finite linear combination; and a generating family gives the quotient onto the whole module. For a finite module, `seedFinrank` is the least `n` admitting a surjection from `Fin n →₀ A`.

**Exclusions:** The natural-valued minimum is asserted only under module finiteness. No finite basis or executable presentation matrix is produced.

`Komorebi.SeedRankBasics.multiSeedQuotientEquivRange`  
definition at `source/main/KomorebiVerification/SeedRankBasics.lean:256`. Signature log starts at line 62. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SeedRankBasics.multiSeedQuotientEquivRange_apply_mk`  
theorem at `source/main/KomorebiVerification/SeedRankBasics.lean:267`. Signature log starts at line 69. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SeedRankBasics.multiSeedQuotientEquiv`  
definition at `source/main/KomorebiVerification/SeedRankBasics.lean:275`. Signature log starts at line 77. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SeedRankOperations.seedFinrank_isLeast_free_surjection`  
theorem at `source/main/KomorebiVerification/SeedRankOperations.lean:62`. Signature log starts at line 84. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 3 — Cyclic characterization

**Contract scope:** For every nontrivial module over a semiring, unrestricted cardinal-valued seed rank equals one exactly when a cyclic vector exists.

**Exclusions:** The zero module is excluded here and is governed separately by `seedRank_eq_zero_iff`.

`Komorebi.SeedRankOperations.cyclic_iff_seedRank_eq_one`  
theorem at `source/main/KomorebiVerification/SeedRankOperations.lean:94`. Signature log starts at line 91. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 4 — Quotient monotonicity

**Contract scope:** For an arbitrary ring homomorphism `σ : A →+* B`, a surjective `σ`-semilinear map gives `seedRank B N ≤ seedRank A M`; `σ` need not be onto.

**Exclusions:** No equality is claimed from surjectivity of the module map alone.

`Komorebi.SeedRankOperations.seedRank_le_of_surjective_semilinear`  
theorem at `source/main/KomorebiVerification/SeedRankOperations.lean:128`. Signature log starts at line 95. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 5 — Image-algebra invariance

**Contract scope:** For a `k`-algebra homomorphism `φ : A →ₐ[k] B` and a bijective `φ`-semilinear map, the target action is restricted literally to `φ.range`, and its seed rank equals the source seed rank.

**Exclusions:** Equality for the full target algebra `B` requires `φ` to be surjective; it is not inferred otherwise.

`Komorebi.SeedRankOperations.seedRank_imageAlgebra_eq`  
theorem at `source/main/KomorebiVerification/SeedRankOperations.lean:188`. Signature log starts at line 102. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 6 — Shared direct-sum bound

**Contract scope:** One semiring acting diagonally on `M × N` gives the cardinal inequality `seedRank A (M × N) ≤ seedRank A M + seedRank A N`.

**Exclusions:** This is only an upper bound; it does not identify when equality holds.

`Komorebi.SeedRankOperations.seedRank_prod_le_add`  
theorem at `source/main/KomorebiVerification/SeedRankOperations.lean:252`. Signature log starts at line 109. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 7 — Independent direct-sum formula

**Contract scope:** With the coordinatewise action of `A × B` on `M × N`, the cardinal seed rank is the maximum of the two component ranks.

**Exclusions:** This formula is not for a single shared diagonal action.

`Komorebi.SeedRankOperations.seedRank_prod_productAlgebra`  
theorem at `source/main/KomorebiVerification/SeedRankOperations.lean:413`. Signature log starts at line 115. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 8 — Tensor-product bound

**Contract scope:** Over a commutative semiring `k`, with the stated algebra/module, scalar-tower, and commuting-action laws, the action of `A ⊗[k] B` on `X ⊗[k] Y` satisfies the cardinal product bound and realizes `(a ⊗ b)(x ⊗ y) = ax ⊗ by`.

**Exclusions:** No equality, completed tensor product, or alternative topological tensor norm is claimed.

`Komorebi.SeedRankOperations.tensorOperator_smul_tmul`  
theorem at `source/main/KomorebiVerification/SeedRankOperations.lean:525`. Signature log starts at line 120. Axioms: `propext`, `Quot.sound`.

`Komorebi.SeedRankOperations.seedRank_tensorProduct_le_mul`  
theorem at `source/main/KomorebiVerification/SeedRankOperations.lean:579`. Signature log starts at line 128. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 9 — Scalar quotient obstruction

**Contract scope:** For a field `k`, a character `χ : A →ₐ[k] k`, a finite-dimensional scalar module `Y`, and a surjective `χ`-semilinear map `X → Y`, `finrank k Y` is a cardinal lower bound for `seedRank A X`.

**Exclusions:** The target action must factor through the stated character; a general quotient does not yield the dimension bound.

`Komorebi.SeedRankOperations.finrank_le_seedRank_of_scalar_quotient`  
theorem at `source/main/KomorebiVerification/SeedRankOperations.lean:618`. Signature log starts at line 137. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 10 — Semisimple multiplicity formula

**Contract scope:** For a finite product, positive block sizes `d i`, a supplied algebra equivalence to the product of full matrix algebras, and a compatible supplied semilinear module equivalence to the product of `d i × m i` matrix modules, seed rank is `max_i ⌈m i / d i⌉`.

**Exclusions:** Lean does not prove the existence of the Wedderburn/module decompositions, nor the nonsplit division-algebra variant.

`Komorebi.SemisimpleCompletion.semisimple_seedRank_eq_maxCeilDiv_of_equivalences`  
theorem at `source/main/KomorebiVerification/SemisimpleCompletion.lean:343`. Signature log starts at line 145. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SemisimpleCompletion.splitProduct_seedRank_eq_maxCeilDiv`  
theorem at `source/main/KomorebiVerification/SemisimpleCompletion.lean:282`. Signature log starts at line 157. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 11 — Full matrix algebra

**Contract scope:** Over a field and for `n > 0`, every nonzero vector in the natural `M_n(k)`-module generates and the canonical cardinal seed rank is one.

**Exclusions:** No statement is made for `n = 0` or for a smaller acting subalgebra.

`Komorebi.SemisimpleCompletion.fullMatrix_every_nonzero_vector_generates`  
theorem at `source/main/KomorebiVerification/SemisimpleCompletion.lean:387`. Signature log starts at line 166. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SemisimpleCompletion.fullMatrix_seedRank_eq_one`  
theorem at `source/main/KomorebiVerification/SemisimpleCompletion.lean:406`. Signature log starts at line 172. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 12 — Multiplicity obstruction

**Contract scope:** For `d > 0`, the left action of `M_d(k)` on the `d × m` matrix realization of `m` copies has seed rank `⌈m/d⌉`; every generating `r`-family satisfies `⌈m/d⌉ ≤ r`.

**Exclusions:** No general simple-module formula over a nontrivial endomorphism division algebra is included.

`Komorebi.SemisimpleCompletion.multiplicity_obstruction`  
theorem at `source/main/KomorebiVerification/SemisimpleCompletion.lean:434`. Signature log starts at line 175. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SemisimpleCompletion.multiplicity_seedRank_formula`  
theorem at `source/main/KomorebiVerification/SemisimpleCompletion.lean:446`. Signature log starts at line 182. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 13 — Single-operator seed rank

**Contract scope:** Certificate-explicit: a finite label family supplies block generators, an attained bound `R`, joint polynomial-orbit generation, polynomial extraction from padded seeds, and surjective scalar quotient maps with the evaluation intertwining law. Then `R` is the least polynomial seed number and both `seedFinrank` and cardinal `seedRank` over the genuine image algebra `k[T] = Algebra.adjoin k {T}` equal `R`.

**Exclusions:** Lean does not construct a primary/Jordan decomposition, Chinese-remainder projectors, or identify the supplied multiplicities with `dim ker(T - λI)` from bare hypotheses.

`Komorebi.SingleOperatorGraph.singleOperator_seedNumber_isLeast_of_primary_decomposition`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:459`. Signature log starts at line 189. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SingleOperatorGraph.singleOperator_operatorAlgebra_seedRanks_eq_of_primary_decomposition`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:493`. Signature log starts at line 214. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 14 — Cyclic matrix criterion

**Contract scope:** Certificate-explicit and finite-dimensional: from an exact positive seed-number certificate, a supplied equality between geometric and block multiplicities, and the supplied minpoly/charpoly canonical-form bridge, Lean proves the four-way equivalence among cyclicity, all geometric multiplicities one, one block per eigenvalue, and `minpoly = charpoly`. The compiled implication does not require the manuscript's separately inherited finite-label hypothesis.

**Exclusions:** Neither canonical-form bridge is derived by Lean from an arbitrary matrix; the theorem verifies the equivalence after those bridges are supplied.

`Komorebi.SingleOperatorGraph.cyclic_matrix_criterion_of_primary_decomposition`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:573`. Signature log starts at line 240. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SingleOperatorGraph.cyclic_matrix_four_way_iff_of_primary_decomposition`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:600`. Signature log starts at line 253. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 15 — Exact packet coordinates

**Contract scope:** A finite complete, idempotent, pairwise-annihilating linear projector family gives mutually inverse analysis and finite-sum synthesis maps between the module and the independently defined dependent product of projector ranges.

**Exclusions:** No infinite summation or topological convergence assertion is present in this algebraic declaration.

`Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis`  
theorem at `source/main/KomorebiVerification/ExactCoordinates.lean:62`. Signature log starts at line 273. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis`  
theorem at `source/main/KomorebiVerification/ExactCoordinates.lean:69`. Signature log starts at line 283. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates`  
definition at `source/main/KomorebiVerification/ExactCoordinates.lean:83`. Signature log starts at line 294. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 16 — Packetwise equality

**Contract scope:** For a finite linear projector family, `x = y` iff every projected packet coordinate agrees.

**Exclusions:** Finiteness and completeness of the packet family remain essential hypotheses.

`Komorebi.PacketNaturalityCompletion.Packets.eq_iff_projectors_eq`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:49`. Signature log starts at line 302. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 17 — Topological packet isomorphism

**Contract scope:** For a finite bounded projector family on a Banach space over a nontrivially normed field, all packet ranges are closed and analysis/synthesis form a continuous linear equivalence with the canonical finite dependent-product norm.

**Exclusions:** No infinite packet family, unbounded projector, or assertion about every arbitrarily chosen equivalent product norm is included.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_packet_isomorphism`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:121`. Signature log starts at line 312. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.packetEquiv`  
definition at `source/main/KomorebiVerification/TopologicalCompletion.lean:107`. Signature log starts at line 326. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 18 — Completion preserves a finite packet split

**Contract scope:** If `M` is a dense submodule of a normed space and `P_i` is any bounded idempotent, the closure of `P_i(M)` equals the full range `P_i(X)`. The packet-family theorem is the direct specialization. No invariance of `M`, surrounding finite packet family, or completeness of `X` is required by the manuscript or the compiled declaration.

**Exclusions:** Boundedness is required; no unbounded-projector or infinite conditional-sum claim is made.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.idempotentRange_eq_closure_map`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:135`. Signature log starts at line 335. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.packetRange_eq_closure_map`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:157`. Signature log starts at line 345. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 19 — Exact operator reconstruction

**Contract scope:** The sum of all transfer blocks reconstructs an arbitrary linear map between modules carrying possibly different finite projector families; the endomorphism formula is the manuscript instance.

**Exclusions:** This is algebraic finite reconstruction, not convergence of an infinite block expansion.

`Komorebi.Foundation.transferBlock_reconstruction_linearMap`  
theorem at `source/main/KomorebiVerification/PaperIBlockCompletion.lean:29`. Signature log starts at line 358. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.Foundation.transferBlock_reconstruction_end`  
theorem at `source/main/KomorebiVerification/PaperIBlockCompletion.lean:39`. Signature log starts at line 364. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 20 — Packet matrix multiplication

**Contract scope:** The block of a composite is the finite sum of composite blocks, even for three different source/intermediate/target modules and projector families; the single-space operator identity is the manuscript instance.

**Exclusions:** No infinite matrix multiplication or operator-norm convergence claim is made.

`Komorebi.Foundation.transferBlock_comp_linearMap`  
theorem at `source/main/KomorebiVerification/PaperIBlockCompletion.lean:48`. Signature log starts at line 369. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.Foundation.transferBlock_comp_end`  
theorem at `source/main/KomorebiVerification/PaperIBlockCompletion.lean:62`. Signature log starts at line 381. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.Foundation.end_comp_eq_sum_transferBlock_comps`  
theorem at `source/main/KomorebiVerification/PaperIBlockCompletion.lean:70`. Signature log starts at line 389. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 21 — Packet powers

**Contract scope:** For every natural power `m`, including `m = 0`, the transfer block of `T^m` equals the recursively defined finite sum over length-`m` packet paths.

**Exclusions:** Only finite powers and finite packet sets are covered.

`Komorebi.PacketNaturalityCompletion.Packets.transferBlock_pow_eq_packetPathSum`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:96`. Signature log starts at line 399. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 22 — Adjoint reversal

**Contract scope:** On a complete real or complex inner-product space, bounded self-adjoint maps satisfy `(Pβ T Pα)† = Pα T† Pβ`. This is stronger than the packet-projector formulation because no idempotence, mutual annihilation, or completeness of a projector family is used.

**Exclusions:** Self-adjointness of both outer maps and boundedness/completeness needed by the adjoint API are explicit.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.adjoint_transferBlock`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:172`. Signature log starts at line 407. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 23 — Algebraic full block representation

**Contract scope:** A finite projector family over a commutative semiring identifies ambient endomorphisms with the genuine dependent family of all packet-to-packet linear maps; transported multiplication is exactly the output-first block product.

**Exclusions:** This is the algebraic endomorphism algebra. Arbitrary algebraic blocks are not asserted to be bounded in a Banach realization.

`Komorebi.PacketNaturalityCompletion.FullBlocks.fullBlockAlgEquiv`  
definition at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:298`. Signature log starts at line 420. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.FullBlocks.restrictBlocks_synthesizeBlocks`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:204`. Signature log starts at line 428. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.FullBlocks.synthesizeBlocks_restrictBlocks`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:231`. Signature log starts at line 439. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.FullBlocks.packetBlockAlgebra_mul_eq_blockMul`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:330`. Signature log starts at line 449. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 24 — Dimension count

**Contract scope:** For a finite-dimensional vector space over a field, endomorphism dimension equals the double sum of packet-dimension products, which equals the square of the packet-dimension sum.

**Exclusions:** No dimension statement for infinite-dimensional or topological dimensions is made.

`Komorebi.PacketNaturalityCompletion.FullBlocks.end_finrank_eq_packet_sum_eq_square`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:381`. Signature log starts at line 458. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.FullBlocks.finrank_eq_sum_packet_finrank`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:352`. Signature log starts at line 485. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 25 — Algebraic packet support pattern

**Contract scope:** Over a field, with every packet range nontrivial and arbitrary packet-Hom blocks allowed, the identity is supported exactly for reflexive relations and universal multiplication closure holds exactly for transitive relations.

**Exclusions:** The converse is not promoted to arbitrary bounded/continuous categories without enough nonzero composable maps.

`Komorebi.PacketNaturalityCompletion.FullBlocks.identity_blocks_supported_iff_reflexive`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:524`. Signature log starts at line 495. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.FullBlocks.blockMulClosed_iff_transitive`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:494`. Signature log starts at line 507. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 26 — Reachability obstruction

**Contract scope:** Word orbits from packet-supported seeds stay in the reflexive-transitive reachable support, and a nontrivial unreachable packet makes the algebraic hull proper. Separately, if the algebraic hull lies in the kernel of a nonzero bounded projector, its closure also lies there and is not dense.

**Exclusions:** The analytic theorem consumes the algebraically proved kernel inclusion; it does not infer graph reachability on its own. No general source-count lower bound is claimed for mixed-packet seeds.

`Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:662`. Signature log starts at line 518. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:675`. Signature log starts at line 532. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.closure_le_ker_of_le_ker`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:184`. Signature log starts at line 545. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_reachability_obstruction`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:190`. Signature log starts at line 553. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 27 — Coordinate transport

**Contract scope:** A linear equivalence transports a finite projector family and conjugates every transfer block. For the conjugated operator family, every zero/nonzero edge and every reflexive-transitive reachability statement is preserved.

**Exclusions:** The full invariance assertion requires invertible coordinate transport, not an arbitrary noninjective map.

`Komorebi.Foundation.LinearProjectorFamily.conjugate`  
definition at `source/main/KomorebiVerification/PaperITransport.lean:27`. Signature log starts at line 561. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.Foundation.conjugate_transferBlock`  
theorem at `source/main/KomorebiVerification/PaperITransport.lean:60`. Signature log starts at line 566. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.Reachability.conjugate_transferEdge_iff`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:721`. Signature log starts at line 577. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.Reachability.conjugate_reachableFrom_iff`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:735`. Signature log starts at line 588. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 28 — Naturality of generation and packets

**Contract scope:** For a strict morphism over a field, generated hulls are natural over the exact image algebra, packet analysis and blocks intertwine, a surjective realization gives the cardinal rank inequality, bijective realization/algebra maps give equality, and bijective packet transport gives complete edge/zero-pattern correspondence. These conclusions do not require the manuscript's finite-dimensional hypothesis.

**Exclusions:** Packet merging is excluded by the injective label map. Full target-algebra rank equality and full target edge coverage require the stated surjectivity/bijectivity hypotheses.

`Komorebi.PacketNaturalityCompletion.StrictNaturality.generatedHull_natural`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:924`. Signature log starts at line 600. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_naturality_package`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:1088`. Signature log starts at line 615. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_le`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:867`. Signature log starts at line 652. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_eq_of_bijective`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:879`. Signature log starts at line 666. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.PacketNaturalityCompletion.StrictNaturality.full_transfer_edge_zero_pattern_correspondence`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:1067`. Signature log starts at line 684. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 29 — Dense realization theorem

**Contract scope:** For normed spaces and bounded operator families, a continuous surjection that sends each source operator into the target family and intertwines it sends a dense source operator hull to a dense target hull. A surjective map intertwining bounded projectors maps the source range onto the target range.

**Exclusions:** No algebra-homomorphism law, openness, or completeness is needed or concluded. Surjectivity is sufficient for the stated conclusions; dense range alone suffices for the density conclusion, but not for exact range equality. The algebraic hulls need not be equal as sets. The range equality itself needs only an intertwining surjective map; it does not require idempotence.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.dense_operatorHull_image`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:251`. Signature log starts at line 721. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.map_packetRange_eq`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:264`. Signature log starts at line 752. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 30 — Typed reachability certificate

**Contract scope:** For the displayed `U = k²`, `V = k³` quiver realization, Lean proves `BA = id`, exhibits the nonzero missing direction in `ker B` but outside `range A`, proves every `U`-supported family insufficient, and proves that the displayed two seeds generate.

**Exclusions:** This is a certificate for the stated finite model, not a classification or minimum-seed theorem for arbitrary quivers.

`Komorebi.PacketNaturalityCompletion.TypedQuiver.typed_reachability_certificate`  
theorem at `source/main/KomorebiVerification/PacketNaturalityCompletion.lean:1357`. Signature log starts at line 767. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 31 — Bilateral-shift seed

**Contract scope:** For the explicit reindexing representation on `ℓ²(ℤ, 𝕂)`, `(S_m x)(n) = x(n-m)`, the orbit of `δ₀` is dense and one is the least finite cardinality of a densely generating seed set.

**Exclusions:** This does not define or equate an unrestricted cardinal-valued Laurent-algebra rank, and it does not formalize the later residue-packet discussion.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.BilateralShiftRepresentation.concretePower_apply`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:435`. Signature log starts at line 791. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.concreteBilateralShift_topologicallyCyclic`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:584`. Signature log starts at line 802. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.concreteBilateralShift_seedCardinality_isLeast`  
theorem at `source/main/KomorebiVerification/TopologicalCompletion.lean:611`. Signature log starts at line 812. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 32 — Graph seed rank, path, and cycle

**Contract scope:** Certificate-explicit general formula: a finite eigenbasis grouped by multiplicity, an attained maximum `R`, and either explicit polynomial projectors or distinct eigenvalue labels prove that `R` is the least operator-seed number; the bridge declarations identify it with both canonical ranks over `k[A]`. Independently, every nonempty path (`n+1` vertices) has minimum one from an endpoint over any field, and every complex simple cycle (`n+3` vertices) has minimum two.

**Exclusions:** Lean does not derive the eigenbasis from the bare assertion that a matrix is symmetric, nor identify an arbitrary graph's algebraic multiplicities without supplied spectral data. The unqualified spectral theorem remains cited classical input.

`Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:794`. Signature log starts at line 825. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity_of_distinct`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:816`. Signature log starts at line 845. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SingleOperatorGraph.operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:266`. Signature log starts at line 858. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SingleOperatorGraph.operatorAlgebra_seedRank_eq_of_seedNumber_isLeast`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:312`. Signature log starts at line 865. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SingleOperatorGraph.path_endpoint_seedNumber_isLeast_one`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:836`. Signature log starts at line 872. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.SingleOperatorGraph.complex_cycle_seedNumber_isLeast_two`  
theorem at `source/main/KomorebiVerification/SingleOperatorGraph.lean:1135`. Signature log starts at line 880. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 33 — Orbit-hull algorithm

**Contract scope:** For a finite operator index on a finite-dimensional vector space over a field and any seed set, the ascending subspace iteration stops after finitely many passes, and the stopped subspace equals the least invariant subspace containing the seeds.

**Exclusions:** The proof is a mathematical termination/correctness specification; it does not extract the paper's basis-maintenance/rank-test implementation or prove a complexity bound.

`Komorebi.FiniteAlgorithms.orbitHull_algorithm_terminates_and_correct`  
theorem at `source/main/KomorebiVerification/EllipticAlgorithms.lean:499`. Signature log starts at line 888. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.FiniteAlgorithms.orbitClosureIter_eq_orbitHull_of_stop`  
theorem at `source/main/KomorebiVerification/EllipticAlgorithms.lean:483`. Signature log starts at line 899. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 34 — Transfer-block algorithm

**Contract scope:** For finite source and target projector families, the table is exactly all transfer blocks, summing it reconstructs the input linear map, and its support predicate is exactly block nonvanishing.

**Exclusions:** No decidable zero-test, sparse edge-list extractor, floating-point tolerance, or runtime bound is verified.

`Komorebi.FiniteAlgorithms.transferBlockTable`  
definition at `source/main/KomorebiVerification/EllipticAlgorithms.lean:530`. Signature log starts at line 910. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.FiniteAlgorithms.assembleTransferBlockTable`  
definition at `source/main/KomorebiVerification/EllipticAlgorithms.lean:537`. Signature log starts at line 916. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.FiniteAlgorithms.transferBlock_algorithm_correct`  
theorem at `source/main/KomorebiVerification/EllipticAlgorithms.lean:542`. Signature log starts at line 921. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.FiniteAlgorithms.transferGraph_iff_block_ne_zero`  
theorem at `source/main/KomorebiVerification/EllipticAlgorithms.lean:556`. Signature log starts at line 930. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

## Row 35 — Exact graph seed-rank algorithm

**Contract scope:** For a finite square matrix over a field, supplied exact eigenbasis, polynomial-projector, spectrum-coverage, eigenspace-dimension, and attained-maximum certificates prove that the finite-spectrum maximum computed by `exactGraphSeedRank` is the least operator-seed number.

**Exclusions:** `exactGraphSeedRank` is noncomputable in Lean. No verified eigensolver, symbolic factorization routine, symmetry-to-diagonalization step, code extraction, or performance guarantee is claimed.

`Komorebi.FiniteAlgorithms.exactGraphSeedRank`  
definition at `source/main/KomorebiVerification/EllipticAlgorithms.lean:594`. Signature log starts at line 938. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

`Komorebi.FiniteAlgorithms.exactGraphSeedRank_isLeast`  
theorem at `source/main/KomorebiVerification/EllipticAlgorithms.lean:610`. Signature log starts at line 941. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

