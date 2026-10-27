# Paper I: expanded publication-to-Lean coverage, Block 02

All **108** current stable records are accounted for. The proof-level denominator is **69**, not 108.

This is a semantic crosswalk, not a new kernel pass for every publication claim. Partial records include missing constructions as well as outstanding wrappers around existing results. No aggregate completion percentage is asserted.

## Status counts

{
  "not_mapped": 20,
  "partial": 34,
  "covered": 15
}

The remaining 39 records are definitions, classical inputs, boundaries and a remark. Their separate statuses are retained in JSON.

## Record-by-record map

### 001 · PSC-I-D-COEFFICIENT-REGIME
**Coefficient and module regimes** · definition · **documentary**

Regime declarations are distributed through Lean typeclass hypotheses, not one encoded regime object.

Source: `editable/traditional/02_foundations.tex:7-10`.

### 002 · PSC-I-D-THEOREM-RECORD
**Canonical theorem record** · definition · **documentary**

Publication metadata. JSON records are not Lean proof declarations.

Source: `editable/traditional/02_foundations.tex:14-22`.

### 003 · PSC-I-B-SYMBOLIC-SCOPE
**Symbolic scope** · boundary · **scope_boundary**

Scope exclusion, not an additional positive theorem.

Source: `editable/traditional/02_foundations.tex:25-28`.

### 004 · PSC-I-D-TYPED-GRAMMAR
**Typed operator grammar** · definition · **not_mapped**

General quiver path algebra, relation ideal, realizations and their morphisms are not encoded in this tranche.

Source: `editable/traditional/02_foundations.tex:37-57`.

### 005 · PSC-I-D-COLLAPSED-REALIZATION
**Collapsed one-space realization** · definition · **partial**

Finite packet coordinates exist for supplied projectors. The collapse of an arbitrary typed grammar is not constructed.

Source: `editable/traditional/02_foundations.tex:60-67`.

Existing contract rows: 15.

Declarations: `Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis`, `Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis`, `Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates`.

### 006 · PSC-I-T-TYPED-MODULE-EQUIVALENCE
**Typed realization and module equivalence** · theorem · **not_mapped**

Missing category definitions, the two functors, and natural inverse isomorphisms for arbitrary typed grammars.

Source: `editable/traditional/02_foundations.tex:70-80`.

### 007 · PSC-I-D-REALIZED-ALGEBRA
**Realized operator algebra** · definition · **partial**

Actual range algebras and k[T] exist. The range of an arbitrary grammar action still needs the grammar construction.

Source: `editable/traditional/02_foundations.tex:114-121`.

Existing contract rows: 5, 13.

Declarations: `Komorebi.SeedRankOperations.seedRank_imageAlgebra_eq`, `Komorebi.SingleOperatorGraph.singleOperator_seedNumber_isLeast_of_primary_decomposition`, `Komorebi.SingleOperatorGraph.singleOperator_operatorAlgebra_seedRanks_eq_of_primary_decomposition`.

### 008 · PSC-I-P-ACTION-FACTORIZATION
**Action factorization and hull invariance** · proposition · **partial**

Image-algebra rank invariance and exact-image hull naturality are proved. The general grammar-action factorization is not assembled.

Source: `editable/traditional/02_foundations.tex:124-131`.

Existing contract rows: 5, 28.

Declarations: `Komorebi.SeedRankOperations.seedRank_imageAlgebra_eq`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.generatedHull_natural`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_naturality_package`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_le`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_eq_of_bijective`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.full_transfer_edge_zero_pattern_correspondence`.

### 009 · PSC-I-D-SEED-SYSTEM
**Linear seed system** · definition · **partial**

Modules, seeds and packets are encoded separately. A full seeded-system object with topology and declared grammar is absent.

Source: `editable/traditional/02_foundations.tex:145-152`.

Existing contract rows: 1, 2, 15.

Declarations: `Komorebi.SeedRankBasics.oneSeedQuotientEquivRange`, `Komorebi.SeedRankBasics.oneSeedQuotientEquivRange_apply_mk`, `Komorebi.SeedRankBasics.generates_singleton_iff_surjective`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_intertwines`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_unique`, `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange`, `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange_apply_mk`, `Komorebi.SeedRankBasics.multiSeedQuotientEquiv`, `Komorebi.SeedRankOperations.seedFinrank_isLeast_free_surjection`, `Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis`, `Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis`, `Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates`.

### 010 · PSC-I-D-GENERATED-HULL
**Generated hull** · definition · **partial**

Algebraic span and normed operator hulls exist. The full Hausdorff topological-vector-space version is not encoded.

Source: `editable/traditional/02_foundations.tex:155-166`.

Existing contract rows: 2, 29.

Declarations: `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange`, `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange_apply_mk`, `Komorebi.SeedRankBasics.multiSeedQuotientEquiv`, `Komorebi.SeedRankOperations.seedFinrank_isLeast_free_surjection`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.dense_operatorHull_image`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.map_packetRange_eq`.

### 011 · PSC-I-D-NATURAL-PRESENTATION
**Natural presentation** · definition · **documentary**

A methodological criterion rather than a decidable Lean predicate.

Source: `editable/traditional/02_foundations.tex:171-174`.

### 012 · PSC-I-P-ALGEBRA-MODULE-GENERATION
**Algebra generation and module generation are distinct** · proposition · **not_mapped**

The general regular-module seed-rank-one corollary still needs a mapped wrapper. It is not the field-only full-matrix result.

Source: `editable/traditional/02_foundations.tex:177-184`.

### 013 · PSC-I-B-TARGET-DEPENDENT-OPERATORS
**Target-dependent operators** · boundary · **scope_boundary**

Target-independence restriction remains documentary.

Source: `editable/traditional/02_foundations.tex:192-195`.

### 014 · PSC-I-D-SEED-EVALUATION
**Seed evaluation map** · definition · **definition_represented**

multiSeedMap is the actual Finsupp linear combination map; finite families give the stated finite free module.

Source: `editable/traditional/02_foundations.tex:215-223`.

Existing contract rows: 2.

Declarations: `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange`, `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange_apply_mk`, `Komorebi.SeedRankBasics.multiSeedQuotientEquiv`, `Komorebi.SeedRankOperations.seedFinrank_isLeast_free_surjection`.

### 015 · PSC-I-T-FREE-PRESENTATION
**Finite free presentation** · theorem · **covered**

Actual range/span equality, quotient equivalence and generation/surjectivity equivalence are present.

Source: `editable/traditional/02_foundations.tex:226-239`.

Existing contract rows: 2.

Declarations: `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange`, `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange_apply_mk`, `Komorebi.SeedRankBasics.multiSeedQuotientEquiv`, `Komorebi.SeedRankOperations.seedFinrank_isLeast_free_surjection`.

### 016 · PSC-I-C-MINIMAL-FREE-COVER
**Minimal free-cover characterization** · corollary · **covered**

seedFinrank_isLeast_free_surjection proves the finite minimum, not an executable basis algorithm.

Source: `editable/traditional/02_foundations.tex:267-275`.

Existing contract rows: 2.

Declarations: `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange`, `Komorebi.SeedRankBasics.multiSeedQuotientEquivRange_apply_mk`, `Komorebi.SeedRankBasics.multiSeedQuotientEquiv`, `Komorebi.SeedRankOperations.seedFinrank_isLeast_free_surjection`.

### 017 · PSC-I-C-ONE-SEED-PRESENTATION
**One-seed presentation** · corollary · **covered**

oneSeedMap has the stated annihilator kernel and its quotient is the literal cyclic range.

Source: `editable/traditional/02_foundations.tex:283-293`.

Existing contract rows: 1.

Declarations: `Komorebi.SeedRankBasics.oneSeedQuotientEquivRange`, `Komorebi.SeedRankBasics.oneSeedQuotientEquivRange_apply_mk`, `Komorebi.SeedRankBasics.generates_singleton_iff_surjective`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_intertwines`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_unique`.

### 018 · PSC-I-P-ANNIHILATOR-TWO-SIDED
**Two-sided annihilator criterion** · proposition · **partial**

New polynomial-module cyclic-annihilator equality is proved. The arbitrary noncommutative ring two-sidedness criterion is not yet proved.

Source: `editable/traditional/02_foundations.tex:302-312`.

Declarations: `Komorebi.PaperICompletion.CyclicClassification.orbitMap_ker_eq_annihilator_of_surjective`.

### 019 · PSC-I-T-COMPLETED-PRESENTATION
**Completion of a dense free presentation** · theorem · **partial**

The normed isometry/dense-completion theorem is proved from supplied input maps. Constructing the transported locally convex topology and its action remains.

Source: `editable/traditional/02_foundations.tex:333-347`.

Existing contract rows: 1.

Declarations: `Komorebi.SeedRankBasics.oneSeedQuotientEquivRange`, `Komorebi.SeedRankBasics.oneSeedQuotientEquivRange_apply_mk`, `Komorebi.SeedRankBasics.generates_singleton_iff_surjective`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_intertwines`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_unique`.

### 020 · PSC-I-D-SEED-RANK
**Seed rank** · definition · **partial**

General algebraic cardinal rank is encoded, including zero. General topological cardinal rank is not; the bilateral-shift finite minimum is a separate example.

Source: `editable/traditional/02_foundations.tex:370-381`.

Existing contract rows: 3, 31.

Declarations: `Komorebi.SeedRankOperations.cyclic_iff_seedRank_eq_one`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.BilateralShiftRepresentation.concretePower_apply`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.concreteBilateralShift_topologicallyCyclic`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.concreteBilateralShift_seedCardinality_isLeast`.

### 021 · PSC-I-P-CYCLIC-CHARACTERIZATION
**Cyclic characterization** · proposition · **covered**

The nontriviality hypothesis agrees with the current publication.

Source: `editable/traditional/02_foundations.tex:384-392`.

Existing contract rows: 3.

Declarations: `Komorebi.SeedRankOperations.cyclic_iff_seedRank_eq_one`.

### 022 · PSC-I-P-ACTING-ALGEBRA-MONOTONICITY
**Monotonicity under enlargement of the acting algebra** · proposition · **partial**

Algebraic rank monotonicity follows through the semilinear identity specialization. General topological rank and a combined wrapper remain.

Source: `editable/traditional/02_foundations.tex:400-407`.

Existing contract rows: 4.

Declarations: `Komorebi.SeedRankOperations.seedRank_le_of_surjective_semilinear`.

### 023 · PSC-I-T-QUOTIENT-MONOTONICITY
**Quotient monotonicity** · theorem · **partial**

The full algebraic semilinear inequality is proved. The printed general topological-rank clause is broader than the normed dense-hull result.

Source: `editable/traditional/02_foundations.tex:421-440`.

Existing contract rows: 4, 29.

Declarations: `Komorebi.SeedRankOperations.seedRank_le_of_surjective_semilinear`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.dense_operatorHull_image`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.map_packetRange_eq`.

### 024 · PSC-I-C-ISOMORPHISM-INVARIANCE
**Isomorphism invariance** · corollary · **partial**

Algebraic isomorphism invariance is proved. The general topological cardinal-rank clause is not encoded.

Source: `editable/traditional/02_foundations.tex:464-467`.

Existing contract rows: 5, 28.

Declarations: `Komorebi.SeedRankOperations.seedRank_imageAlgebra_eq`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.generatedHull_natural`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_naturality_package`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_le`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_eq_of_bijective`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.full_transfer_edge_zero_pattern_correspondence`.

### 025 · PSC-I-T-EXACT-SEQUENCE-BOUNDS
**Short exact sequence bounds** · theorem · **partial**

The quotient lower bound is available. Lifting generators through an arbitrary exact sequence for the upper bound remains.

Source: `editable/traditional/02_foundations.tex:475-488`.

Existing contract rows: 4.

Declarations: `Komorebi.SeedRankOperations.seedRank_le_of_surjective_semilinear`.

### 026 · PSC-I-P-SHARED-DIRECT-SUM
**Shared direct-sum bounds** · proposition · **partial**

The upper bound is explicit; projection lower bounds have the needed ingredients but the whole two-sided statement has no dedicated wrapper yet.

Source: `editable/traditional/02_foundations.tex:506-516`.

Existing contract rows: 4, 6.

Declarations: `Komorebi.SeedRankOperations.seedRank_le_of_surjective_semilinear`, `Komorebi.SeedRankOperations.seedRank_prod_le_add`.

### 027 · PSC-I-T-INDEPENDENT-DIRECT-SUM
**Independent direct-sum formula** · theorem · **covered**

Actual product-algebra action and the maximum formula are proved.

Source: `editable/traditional/02_foundations.tex:524-538`.

Existing contract rows: 7.

Declarations: `Komorebi.SeedRankOperations.seedRank_prod_productAlgebra`.

### 028 · PSC-I-P-TENSOR-BOUND
**Tensor-product bound** · proposition · **covered**

The genuine tensor-product action and cardinal product upper bound are proved.

Source: `editable/traditional/02_foundations.tex:557-567`.

Existing contract rows: 8.

Declarations: `Komorebi.SeedRankOperations.tensorOperator_smul_tmul`, `Komorebi.SeedRankOperations.seedRank_tensorProduct_le_mul`.

### 029 · PSC-I-B-TENSOR-NONEQUALITY
**Tensor rank is not generally multiplicative** · boundary · **scope_boundary**

No universal tensor equality is exported. This boundary is not counted as a positive theorem.

Source: `editable/traditional/02_foundations.tex:584-587`.

Existing contract rows: 8.

Declarations: `Komorebi.SeedRankOperations.tensorOperator_smul_tmul`, `Komorebi.SeedRankOperations.seedRank_tensorProduct_le_mul`.

### 030 · PSC-I-P-SCALAR-EXTENSION-MONOTONICITY
**Scalar-extension monotonicity** · proposition · **partial**

General tensor generation gives a route. The scalar-extension specialization and the literal 1 tensor S generating family are not assembled.

Source: `editable/traditional/02_foundations.tex:592-607`.

Existing contract rows: 8.

Declarations: `Komorebi.SeedRankOperations.tensorOperator_smul_tmul`, `Komorebi.SeedRankOperations.seedRank_tensorProduct_le_mul`.

### 031 · PSC-I-D-SEED-RANK-WITNESS
**Seed-rank witness** · definition · **documentary**

A named use of the quotient lower bound, not a new proof target.

Source: `editable/traditional/02_foundations.tex:632-635`.

Existing contract rows: 4.

Declarations: `Komorebi.SeedRankOperations.seedRank_le_of_surjective_semilinear`.

### 032 · PSC-I-P-SCALAR-QUOTIENT-WITNESS
**Scalar quotient witness** · proposition · **covered**

The character, surjective semilinear map and finite scalar dimension match the printed hypotheses.

Source: `editable/traditional/02_foundations.tex:638-648`.

Existing contract rows: 9.

Declarations: `Komorebi.SeedRankOperations.finrank_le_seedRank_of_scalar_quotient`.

### 033 · PSC-I-CI-NAKAYAMA
**Nakayama lemma** · classicalinput · **classical_input_not_fully_integrated**

The printed noncommutative Nakayama input is not yet connected by a checked declaration here. Do not silently substitute only a commutative version.

Source: `editable/traditional/02_foundations.tex:669-672`.

### 034 · PSC-I-T-MODULE-TOP
**Generator number is detected modulo the Jacobson radical** · theorem · **not_mapped**

Need the quotient action, radical lifting of generators, and equality of canonical ranks.

Source: `editable/traditional/02_foundations.tex:675-683`.

### 035 · PSC-I-C-LOCAL-ALGEBRA-FORMULA
**Local algebra formula** · corollary · **not_mapped**

Need module-top equality and the residue division-ring dimension bridge.

Source: `editable/traditional/02_foundations.tex:709-718`.

### 036 · PSC-I-CI-WEDDERBURN-ARTIN
**Wedderburn--Artin decomposition** · classicalinput · **classical_input_not_fully_integrated**

The existence of an abstract Wedderburn decomposition is not supplied by the certificate transport theorem.

Source: `editable/traditional/02_foundations.tex:727-734`.

### 037 · PSC-I-L-REGULAR-MODULE-MULTIPLICITIES
**Regular-module multiplicities** · lemma · **partial**

Concrete split-field matrix models exist. The general division-ring regular-module equivalence is not supplied.

Source: `editable/traditional/02_foundations.tex:737-747`.

Existing contract rows: 10.

Declarations: `Komorebi.SemisimpleCompletion.semisimple_seedRank_eq_maxCeilDiv_of_equivalences`, `Komorebi.SemisimpleCompletion.splitProduct_seedRank_eq_maxCeilDiv`.

### 038 · PSC-I-T-SEMISIMPLE-SEED-RANK
**Semisimple seed-rank formula over arbitrary division rings** · theorem · **partial**

Split-field certificate transport is proved. Division-ring factors, abstract decomposition existence and the radical/top reduction remain.

Source: `editable/traditional/02_foundations.tex:759-779`.

Existing contract rows: 10.

Declarations: `Komorebi.SemisimpleCompletion.semisimple_seedRank_eq_maxCeilDiv_of_equivalences`, `Komorebi.SemisimpleCompletion.splitProduct_seedRank_eq_maxCeilDiv`.

### 039 · PSC-I-C-ALGEBRAICALLY-CLOSED-FORMULA
**Algebraically closed multiplicity formula** · corollary · **partial**

The formula on a supplied split model is proved. The printed top quotient requires the module-top bridge.

Source: `editable/traditional/02_foundations.tex:808-820`.

Existing contract rows: 10.

Declarations: `Komorebi.SemisimpleCompletion.semisimple_seedRank_eq_maxCeilDiv_of_equivalences`, `Komorebi.SemisimpleCompletion.splitProduct_seedRank_eq_maxCeilDiv`.

### 040 · PSC-I-C-FULL-MATRIX
**Full matrix algebra** · corollary · **partial**

Proved for positive matrix size over a field. Arbitrary division-ring scalars remain. Positive size is still required.

Source: `editable/traditional/02_foundations.tex:828-835`.

Existing contract rows: 11.

Declarations: `Komorebi.SemisimpleCompletion.fullMatrix_every_nonzero_vector_generates`, `Komorebi.SemisimpleCompletion.fullMatrix_seedRank_eq_one`.

### 041 · PSC-I-C-MULTIPLICITY-OBSTRUCTION
**Multiplicity obstruction** · corollary · **partial**

Proved for field-valued multiplicity matrices and positive block size, not arbitrary division rings.

Source: `editable/traditional/02_foundations.tex:843-853`.

Existing contract rows: 12.

Declarations: `Komorebi.SemisimpleCompletion.multiplicity_obstruction`, `Komorebi.SemisimpleCompletion.multiplicity_seedRank_formula`.

### 042 · PSC-I-CI-PID-PRIMARY-DECOMPOSITION
**Primary decomposition for polynomial modules** · classicalinput · **classical_input_not_fully_integrated**

Mathlib has a proven PID torsion-module decomposition. This block uses its annihilator-attainment consequence, but does not yet instantiate all printed primary components of T.

Source: `editable/traditional/02_foundations.tex:881-888`.

Declarations: `Komorebi.PaperICompletion.CyclicClassification.exists_full_annihilator_vector`.

### 043 · PSC-I-T-SINGLE-OPERATOR
**Single-operator seed rank** · theorem · **partial**

General certificate assembly is retained; the self-adjoint case now constructs the data. General irreducible-polynomial residue quotients and intrinsic primary multiplicities remain.

Source: `editable/traditional/02_foundations.tex:891-905`.

Existing contract rows: 13.

Declarations: `Komorebi.SingleOperatorGraph.singleOperator_seedNumber_isLeast_of_primary_decomposition`, `Komorebi.SingleOperatorGraph.singleOperator_operatorAlgebra_seedRanks_eq_of_primary_decomposition`, `Komorebi.PaperICompletion.SpectralCertificates.selfAdjoint_operatorAlgebra_seedRanks`.

### 044 · PSC-I-C-INVARIANT-FACTOR-COUNT
**Invariant-factor count** · corollary · **partial**

The cyclic one-generator case now has a genuine minpoly quotient construction. The minimum for a general invariant-factor chain remains.

Source: `editable/traditional/02_foundations.tex:949-961`.

Existing contract rows: 13.

Declarations: `Komorebi.SingleOperatorGraph.singleOperator_seedNumber_isLeast_of_primary_decomposition`, `Komorebi.SingleOperatorGraph.singleOperator_operatorAlgebra_seedRanks_eq_of_primary_decomposition`, `Komorebi.PaperICompletion.CyclicClassification.minpolyQuotientEquivOrbit`.

### 045 · PSC-I-C-ALGEBRAICALLY-CLOSED-SINGLE-OPERATOR
**Geometric-multiplicity formula** · corollary · **partial**

Intrinsic eigenspace dimensions and the exact maximum are now proved for self-adjoint operators. Arbitrary non-diagonalizable operators over an algebraically closed field remain.

Source: `editable/traditional/02_foundations.tex:969-980`.

Existing contract rows: 13, 32.

Declarations: `Komorebi.SingleOperatorGraph.singleOperator_seedNumber_isLeast_of_primary_decomposition`, `Komorebi.SingleOperatorGraph.singleOperator_operatorAlgebra_seedRanks_eq_of_primary_decomposition`, `Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity`, `Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity_of_distinct`, `Komorebi.SingleOperatorGraph.operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast`, `Komorebi.SingleOperatorGraph.operatorAlgebra_seedRank_eq_of_seedNumber_isLeast`, `Komorebi.SingleOperatorGraph.path_endpoint_seedNumber_isLeast_one`, `Komorebi.SingleOperatorGraph.complex_cycle_seedNumber_isLeast_two`, `Komorebi.PaperICompletion.SpectralCertificates.selfAdjoint_seedRank_eq_max_eigenspace_finrank`.

### 046 · PSC-I-C-CYCLIC-MATRIX
**Cyclic-matrix criterion** · corollary · **partial**

Cyclicity iff minpoly=charpoly is now unconditional over any field; on nonzero spaces it also equals seed rank one. The primary, invariant-factor and scalar-extension geometric clauses remain.

Source: `editable/traditional/02_foundations.tex:988-999`.

Existing contract rows: 14.

Declarations: `Komorebi.SingleOperatorGraph.cyclic_matrix_criterion_of_primary_decomposition`, `Komorebi.SingleOperatorGraph.cyclic_matrix_four_way_iff_of_primary_decomposition`, `Komorebi.PaperICompletion.CyclicClassification.hasCyclicVector_iff_minpoly_eq_charpoly`, `Komorebi.PaperICompletion.CyclicClassification.operatorAlgebra_seedRank_eq_one_iff_minpoly_eq_charpoly`, `Komorebi.PaperICompletion.CyclicClassification.cyclic_four_way_without_polynomial_certificate`.

### 047 · PSC-I-D-PACKET-SYSTEM
**Finite packet system** · definition · **definition_represented**

LinearProjectorFamily encodes the actual finite completeness, idempotence and annihilation laws.

Source: `editable/traditional/03_packets_and_graphs.tex:10-25`.

Existing contract rows: 15.

Declarations: `Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis`, `Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis`, `Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates`.

### 048 · PSC-I-D-PACKET-SUPPORT
**Packet support and packet-pure vectors** · definition · **partial**

Packet coordinate support is used in reachability arguments. A general packet-purity predicate and its cardinal rank are not encoded.

Source: `editable/traditional/03_packets_and_graphs.tex:28-37`.

Existing contract rows: 26.

Declarations: `Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support`, `Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.closure_le_ker_of_le_ker`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_reachability_obstruction`.

### 049 · PSC-I-L-PACKET-AGGREGATION
**Finite packet aggregation** · lemma · **partial**

The coordinate-fibre refinement example is proved. Aggregating an arbitrary finite projector family and identifying every grouped range remain.

Source: `editable/traditional/03_packets_and_graphs.tex:45-55`.

Declarations: `Komorebi.Packet.fibreLinearProj_refinement`.

### 050 · PSC-I-D-ANALYSIS-SYNTHESIS
**Packet analysis and synthesis** · definition · **definition_represented**

Analysis and synthesis use genuine projector ranges, not unconstrained packet slots.

Source: `editable/traditional/03_packets_and_graphs.tex:69-83`.

Existing contract rows: 15.

Declarations: `Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis`, `Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis`, `Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates`.

### 051 · PSC-I-T-EXACT-PACKET-COORDINATES
**Exact packet-coordinate isomorphism** · theorem · **covered**

Both inverse identities and the linear equivalence are proved.

Source: `editable/traditional/03_packets_and_graphs.tex:86-100`.

Existing contract rows: 15.

Declarations: `Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis`, `Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis`, `Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates`.

### 052 · PSC-I-C-PACKETWISE-EQUALITY
**Packetwise equality** · corollary · **covered**

Exact equality iff every projected coordinate agrees.

Source: `editable/traditional/03_packets_and_graphs.tex:128-136`.

Existing contract rows: 16.

Declarations: `Komorebi.PacketNaturalityCompletion.Packets.eq_iff_projectors_eq`.

### 053 · PSC-I-C-PACKET-UNIVERSAL-PROPERTY
**Universal mapping property of finite packet coordinates** · corollary · **partial**

Coordinate equivalence and all-Hom block equivalence supply ingredients. The two arbitrary-domain/codomain universal properties and uniqueness wrappers remain.

Source: `editable/traditional/03_packets_and_graphs.tex:146-166`.

Existing contract rows: 15, 23.

Declarations: `Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis`, `Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis`, `Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates`, `Komorebi.PacketNaturalityCompletion.FullBlocks.fullBlockAlgEquiv`, `Komorebi.PacketNaturalityCompletion.FullBlocks.restrictBlocks_synthesizeBlocks`, `Komorebi.PacketNaturalityCompletion.FullBlocks.synthesizeBlocks_restrictBlocks`, `Komorebi.PacketNaturalityCompletion.FullBlocks.packetBlockAlgebra_mul_eq_blockMul`.

### 054 · PSC-I-T-TENSOR-PACKET-SYSTEM
**Tensor-product packet systems** · theorem · **not_mapped**

No general tensor projector family, range tensor equivalence, or resulting decomposition is mapped.

Source: `editable/traditional/03_packets_and_graphs.tex:188-210`.

### 055 · PSC-I-P-DUAL-PACKET-SYSTEM
**Dual packet systems** · proposition · **not_mapped**

The algebraic dual family and canonical dual-range identification are not mapped.

Source: `editable/traditional/03_packets_and_graphs.tex:234-246`.

### 056 · PSC-I-T-BANACH-PACKET-ISOMORPHISM
**Finite Banach packet isomorphism** · theorem · **partial**

Closed ranges and bounded inverse maps in the canonical product norm are proved. The universal quantification over all equivalent finite-product norms needs explicit transport.

Source: `editable/traditional/03_packets_and_graphs.tex:267-270`.

Existing contract rows: 17.

Declarations: `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_packet_isomorphism`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.packetEquiv`.

### 057 · PSC-I-D-PACKET-CONDITION-NUMBER
**Packet-coordinate condition number** · definition · **definition_represented**

New conditionNumber is the product of actual operator norms. packetConditionNumber identifies the literal analysis/synthesis norms.

Source: `editable/traditional/03_packets_and_graphs.tex:282-290`.

Declarations: `Komorebi.PaperICompletion.ConditionedCoordinates.conditionNumber`, `Komorebi.PaperICompletion.ConditionedCoordinates.packetConditionNumber_eq`.

### 058 · PSC-I-P-CONDITIONED-COORDINATES
**Conditioned coordinate transport** · proposition · **covered**

New proofs give the lower bound for nonzero X and both operator norm inequalities for an arbitrary bounded coordinate equivalence, hence any declared packet-coordinate norm.

Source: `editable/traditional/03_packets_and_graphs.tex:293-313`.

Declarations: `Komorebi.PaperICompletion.ConditionedCoordinates.one_le_conditionNumber`, `Komorebi.PaperICompletion.ConditionedCoordinates.norm_coordinateOperator_le`, `Komorebi.PaperICompletion.ConditionedCoordinates.norm_le_conditionNumber_mul_coordinateOperator`, `Komorebi.PaperICompletion.ConditionedCoordinates.packet_conditioned_coordinate_bounds`.

### 059 · PSC-I-C-COMPLETION-PACKET-SPLIT
**Completion preserves a finite packet split** · corollary · **partial**

The range/closure identity is fully proved. The printed unique extension of the whole split to completion still needs an explicit wrapper.

Source: `editable/traditional/03_packets_and_graphs.tex:334-341`.

Existing contract rows: 18.

Declarations: `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.idempotentRange_eq_closure_map`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.packetRange_eq_closure_map`.

### 060 · PSC-I-D-UNCONDITIONAL-PACKET-SPACE
**Unconditional packet sum space** · definition · **not_mapped**

The unconditional packet-sum space and its signed-sum norm are not encoded.

Source: `editable/traditional/03_packets_and_graphs.tex:352-366`.

### 061 · PSC-I-L-UNCONDITIONAL-COMPLETENESS
**Completeness of the unconditional packet sum** · lemma · **not_mapped**

Completeness of that specifically defined normed sequence space remains.

Source: `editable/traditional/03_packets_and_graphs.tex:369-372`.

### 062 · PSC-I-T-COUNTABLE-UNCONDITIONAL-PACKETS
**Countable unconditional packet isomorphism** · theorem · **not_mapped**

Countable unconditional synthesis, the inverse maps and the quantitative norm bounds remain.

Source: `editable/traditional/03_packets_and_graphs.tex:407-436`.

### 063 · PSC-I-R-UNIFORM-BOUNDEDNESS
**Uniform boundedness** · remark · **documentary**

A uniform-boundedness explanation. No instance for the signed packet partial-sum family is mapped.

Source: `editable/traditional/03_packets_and_graphs.tex:469-472`.

### 064 · PSC-I-B-INFINITE-PACKET-TOPOLOGY
**Infinite packet sums** · boundary · **scope_boundary**

Convergence modes remain separate; finite identities are not used as infinite sums.

Source: `editable/traditional/03_packets_and_graphs.tex:475-478`.

### 065 · PSC-I-D-TRANSFER-BLOCK
**Transfer block** · definition · **definition_represented**

Ambient compositions and their genuinely range-restricted packet Hom maps are both encoded.

Source: `editable/traditional/03_packets_and_graphs.tex:492-499`.

Existing contract rows: 19, 23.

Declarations: `Komorebi.Foundation.transferBlock_reconstruction_linearMap`, `Komorebi.Foundation.transferBlock_reconstruction_end`, `Komorebi.PacketNaturalityCompletion.FullBlocks.fullBlockAlgEquiv`, `Komorebi.PacketNaturalityCompletion.FullBlocks.restrictBlocks_synthesizeBlocks`, `Komorebi.PacketNaturalityCompletion.FullBlocks.synthesizeBlocks_restrictBlocks`, `Komorebi.PacketNaturalityCompletion.FullBlocks.packetBlockAlgebra_mul_eq_blockMul`.

### 066 · PSC-I-T-OPERATOR-RECONSTRUCTION
**Exact operator reconstruction** · theorem · **covered**

The existing result is more general: source and target can have different finite packet systems.

Source: `editable/traditional/03_packets_and_graphs.tex:502-508`.

Existing contract rows: 19.

Declarations: `Komorebi.Foundation.transferBlock_reconstruction_linearMap`, `Komorebi.Foundation.transferBlock_reconstruction_end`.

### 067 · PSC-I-T-BLOCK-MULTIPLICATION
**Packet matrix multiplication** · theorem · **covered**

The output-first block product is proved for three possibly different modules.

Source: `editable/traditional/03_packets_and_graphs.tex:529-539`.

Existing contract rows: 20.

Declarations: `Komorebi.Foundation.transferBlock_comp_linearMap`, `Komorebi.Foundation.transferBlock_comp_end`, `Komorebi.Foundation.end_comp_eq_sum_transferBlock_comps`.

### 068 · PSC-I-C-BLOCK-POWERS
**Packet powers and paths** · corollary · **partial**

All natural powers, including zero, are proved. Arbitrary nonidentical word products still need the iterated wrapper.

Source: `editable/traditional/03_packets_and_graphs.tex:559-571`.

Existing contract rows: 21.

Declarations: `Komorebi.PacketNaturalityCompletion.Packets.transferBlock_pow_eq_packetPathSum`.

### 069 · PSC-I-C-ADJOINT-REVERSAL
**Adjoint reversal** · corollary · **covered**

The result is proved for bounded self-adjoint outer maps, more generally than orthogonal packet projectors.

Source: `editable/traditional/03_packets_and_graphs.tex:579-585`.

Existing contract rows: 22.

Declarations: `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.adjoint_transferBlock`.

### 070 · PSC-I-C-TENSOR-TRANSFER-BLOCKS
**Tensor-product transfer blocks** · corollary · **not_mapped**

Tensor-block factorization and the general tensor packet construction are not mapped.

Source: `editable/traditional/03_packets_and_graphs.tex:598-608`.

### 071 · PSC-I-T-BLOCK-INTERTWINING
**Blockwise intertwining equations** · theorem · **partial**

Individual intertwining blocks and composition identities are proved. The complete arbitrary-source/target block-equation iff remains.

Source: `editable/traditional/03_packets_and_graphs.tex:623-645`.

Existing contract rows: 20, 28.

Declarations: `Komorebi.Foundation.transferBlock_comp_linearMap`, `Komorebi.Foundation.transferBlock_comp_end`, `Komorebi.Foundation.end_comp_eq_sum_transferBlock_comps`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.generatedHull_natural`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_naturality_package`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_le`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_eq_of_bijective`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.full_transfer_edge_zero_pattern_correspondence`.

### 072 · PSC-I-T-BLOCK-ALGEBRA
**Full block-algebra representation** · theorem · **covered**

Full dependent packet Hom families and their multiplication are identified with the actual endomorphism algebra.

Source: `editable/traditional/03_packets_and_graphs.tex:675-686`.

Existing contract rows: 23.

Declarations: `Komorebi.PacketNaturalityCompletion.FullBlocks.fullBlockAlgEquiv`, `Komorebi.PacketNaturalityCompletion.FullBlocks.restrictBlocks_synthesizeBlocks`, `Komorebi.PacketNaturalityCompletion.FullBlocks.synthesizeBlocks_restrictBlocks`, `Komorebi.PacketNaturalityCompletion.FullBlocks.packetBlockAlgebra_mul_eq_blockMul`.

### 073 · PSC-I-C-PACKET-SUPPORT-PROPAGATION
**Propagation of packet support** · corollary · **partial**

Orbit support obstructions exist. The one-step exact support statement with noncancellation equality conditions is not completely mapped.

Source: `editable/traditional/03_packets_and_graphs.tex:703-720`.

Existing contract rows: 26.

Declarations: `Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support`, `Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.closure_le_ker_of_le_ker`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_reachability_obstruction`.

### 074 · PSC-I-C-DIMENSION-COUNT
**Dimension count** · corollary · **covered**

The two dimension equalities are explicitly proved.

Source: `editable/traditional/03_packets_and_graphs.tex:736-746`.

Existing contract rows: 24.

Declarations: `Komorebi.PacketNaturalityCompletion.FullBlocks.end_finrank_eq_packet_sum_eq_square`, `Komorebi.PacketNaturalityCompletion.FullBlocks.finrank_eq_sum_packet_finrank`.

### 075 · PSC-I-P-BLOCK-DIAGONAL-COMMUTANT
**Block-diagonal projection and packet commutant** · proposition · **not_mapped**

The diagonal projection, its range, idempotence and the three-way commutant criterion remain.

Source: `editable/traditional/03_packets_and_graphs.tex:754-766`.

### 076 · PSC-I-D-SUPPORT-RELATION
**Support relation and support space** · definition · **partial**

A supported full-block predicate exists. The ambient operator support subspace still needs a named transported definition.

Source: `editable/traditional/03_packets_and_graphs.tex:789-797`.

Existing contract rows: 25.

Declarations: `Komorebi.PacketNaturalityCompletion.FullBlocks.identity_blocks_supported_iff_reflexive`, `Komorebi.PacketNaturalityCompletion.FullBlocks.blockMulClosed_iff_transitive`.

### 077 · PSC-I-T-SUPPORT-PATTERN-ALGEBRA
**Support-pattern algebra criterion** · theorem · **partial**

The two hard converses, identity/reflexivity and multiplication/transitivity, are proved. The complete ambient support-subalgebra equivalence is not assembled.

Source: `editable/traditional/03_packets_and_graphs.tex:800-808`.

Existing contract rows: 25.

Declarations: `Komorebi.PacketNaturalityCompletion.FullBlocks.identity_blocks_supported_iff_reflexive`, `Komorebi.PacketNaturalityCompletion.FullBlocks.blockMulClosed_iff_transitive`.

### 078 · PSC-I-C-SUPPORT-PATTERN-STAR
**$*$-closed bounded support patterns** · corollary · **partial**

Adjoint reversal is proved. Bounded supported operators, the converse rank-one construction and star-subalgebra equivalence remain.

Source: `editable/traditional/03_packets_and_graphs.tex:832-839`.

Existing contract rows: 22.

Declarations: `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.adjoint_transferBlock`.

### 079 · PSC-I-T-PREORDER-ALGEBRA-DECOMPOSITION
**Preorder support algebra decomposition** · theorem · **not_mapped**

The class quotient, nilpotent ideal, height bound and diagonal-class quotient algebra are not mapped.

Source: `editable/traditional/03_packets_and_graphs.tex:847-875`.

### 080 · PSC-I-D-TRANSFER-GRAPH
**Transfer graph of an algebra-generating family** · definition · **partial**

Transfer edges and reflexive-transitive reachability are encoded. The exact generating-algebra presentation still needs the projector-generator comparison.

Source: `editable/traditional/03_packets_and_graphs.tex:916-931`.

Existing contract rows: 26.

Declarations: `Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support`, `Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.closure_le_ker_of_le_ker`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_reachability_obstruction`.

### 081 · PSC-I-T-ALGEBRA-REACHABILITY-SUPPORT
**Reachability support of the generated algebra** · theorem · **partial**

Word-hull support is proved. The full generated-algebra block-support statement requires the explicit span/adjoin bridge.

Source: `editable/traditional/03_packets_and_graphs.tex:934-947`.

Existing contract rows: 26.

Declarations: `Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support`, `Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.closure_le_ker_of_le_ker`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_reachability_obstruction`.

### 082 · PSC-I-P-REACHABILITY-OBSTRUCTION
**Reachability obstruction for generated hulls** · proposition · **partial**

The complete orbit-hull obstruction is proved. Aligning that word hull with the printed algebra generated also by packet projectors is a remaining wrapper.

Source: `editable/traditional/03_packets_and_graphs.tex:977-992`.

Existing contract rows: 26.

Declarations: `Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support`, `Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.closure_le_ker_of_le_ker`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_reachability_obstruction`.

### 083 · PSC-I-D-DIRECTED-SEED-RANK
**Packet-pure seed rank** · definition · **not_mapped**

Packet-pure cardinal seed rank and local corner ranks are not encoded.

Source: `editable/traditional/03_packets_and_graphs.tex:1010-1030`.

### 084 · PSC-I-P-PACKET-PURE-RANK-BOUNDS
**Basic packet-pure rank bounds** · proposition · **not_mapped**

Need packet-pure rank and corner-algebra generator assembly.

Source: `editable/traditional/03_packets_and_graphs.tex:1033-1047`.

### 085 · PSC-I-D-EDGE-SURJECTIVE
**Edge-surjective packet system** · definition · **not_mapped**

The general edge-surjectivity predicate and pure-block surjection data are not encoded.

Source: `editable/traditional/03_packets_and_graphs.tex:1055-1062`.

### 086 · PSC-I-T-SOURCE-COMPONENT-SEED-RANK
**Source-component formula for packet-pure seed rank** · theorem · **not_mapped**

Need condensation components, local packet-pure ranks and the source propagation/lower-bound proof.

Source: `editable/traditional/03_packets_and_graphs.tex:1065-1075`.

### 087 · PSC-I-D-PACKET-PROPAGATING
**Packet-propagating system** · definition · **not_mapped**

The combined edge-surjectivity and corner-cyclicity predicate is not encoded.

Source: `editable/traditional/03_packets_and_graphs.tex:1104-1110`.

### 088 · PSC-I-C-SOURCE-COMPONENT-COUNT
**Unweighted source-component count** · corollary · **not_mapped**

Depends on the general source-component theorem and local cyclicity reduction.

Source: `editable/traditional/03_packets_and_graphs.tex:1113-1121`.

### 089 · PSC-I-B-PACKET-PURE-BOUNDARY
**Mixed-support seeds can merge source requirements** · boundary · **scope_boundary**

The unrestricted mixed-seed example is consistent with the proved product-algebra formula. The packet-pure rank calculation is not separately formalized.

Source: `editable/traditional/03_packets_and_graphs.tex:1129-1145`.

Existing contract rows: 7.

Declarations: `Komorebi.SeedRankOperations.seedRank_prod_productAlgebra`.

### 090 · PSC-I-T-COORDINATE-TRANSPORT
**Coordinate transport** · theorem · **partial**

Conjugation of projectors/blocks and graph/reachability invariance are proved. The full packet-dimension and support-preorder wrapper remains.

Source: `editable/traditional/04_transport.tex:7-22`.

Existing contract rows: 27, 28.

Declarations: `Komorebi.Foundation.LinearProjectorFamily.conjugate`, `Komorebi.Foundation.conjugate_transferBlock`, `Komorebi.PacketNaturalityCompletion.Reachability.conjugate_transferEdge_iff`, `Komorebi.PacketNaturalityCompletion.Reachability.conjugate_reachableFrom_iff`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.generatedHull_natural`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_naturality_package`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_le`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_eq_of_bijective`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.full_transfer_edge_zero_pattern_correspondence`.

### 091 · PSC-I-D-PACKET-MORPHISM
**Packet-compatible operator morphism** · definition · **partial**

Strict injective-label morphisms are encoded. Arbitrary label maps and fibre aggregation remain.

Source: `editable/traditional/04_transport.tex:48-68`.

Existing contract rows: 28.

Declarations: `Komorebi.PacketNaturalityCompletion.StrictNaturality.generatedHull_natural`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_naturality_package`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_le`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_eq_of_bijective`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.full_transfer_edge_zero_pattern_correspondence`.

### 092 · PSC-I-D-SEED-MORPHISM
**Morphism of seeded systems** · definition · **not_mapped**

The seeded morphism condition and topological seeded category are not encoded.

Source: `editable/traditional/04_transport.tex:73-84`.

### 093 · PSC-I-T-NATURALITY
**Naturality of generated hulls and transfer blocks** · theorem · **partial**

Exact image-algebra hull naturality and strict block naturality are proved. Noninjective label aggregation and the seeded corollary remain.

Source: `editable/traditional/04_transport.tex:87-109`.

Existing contract rows: 28.

Declarations: `Komorebi.PacketNaturalityCompletion.StrictNaturality.generatedHull_natural`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_naturality_package`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_le`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_eq_of_bijective`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.full_transfer_edge_zero_pattern_correspondence`.

### 094 · PSC-I-P-SEED-SYSTEM-CATEGORY
**Category of seeded packet systems** · proposition · **not_mapped**

General packet and seeded categories, identities and composition laws are not mapped.

Source: `editable/traditional/04_transport.tex:138-141`.

### 095 · PSC-I-T-PACKET-EXACT-SEQUENCE
**Packet exact sequence for an invariant subspace** · theorem · **not_mapped**

Restriction and quotient packet construction, the packetwise short exact sequences and their assembly remain.

Source: `editable/traditional/04_transport.tex:185-216`.

### 096 · PSC-I-T-QUOTIENT-PACKET-DESCENT
**Packet descent through an invariant quotient** · theorem · **not_mapped**

The quotient family must be constructed from invariance, not supplied as an independent family.

Source: `editable/traditional/04_transport.tex:232-243`.

### 097 · PSC-I-C-QUOTIENT-PACKET-DESCENT
**Restriction and quotient of transfer blocks** · corollary · **partial**

Intertwining of supplied families is available. The invariant-subspace restrictions and actual quotient family remain.

Source: `editable/traditional/04_transport.tex:254-265`.

Existing contract rows: 27, 28.

Declarations: `Komorebi.Foundation.LinearProjectorFamily.conjugate`, `Komorebi.Foundation.conjugate_transferBlock`, `Komorebi.PacketNaturalityCompletion.Reachability.conjugate_transferEdge_iff`, `Komorebi.PacketNaturalityCompletion.Reachability.conjugate_reachableFrom_iff`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.generatedHull_natural`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_naturality_package`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_le`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_eq_of_bijective`, `Komorebi.PacketNaturalityCompletion.StrictNaturality.full_transfer_edge_zero_pattern_correspondence`.

### 098 · PSC-I-C-TOPOLOGICAL-PACKET-EXACT-SEQUENCE
**Topological packet exact sequence** · corollary · **not_mapped**

Need bounded quotient projectors, closed packet kernels and Banach exact-sequence maps.

Source: `editable/traditional/04_transport.tex:284-287`.

### 099 · PSC-I-T-DENSE-REALIZATION
**Dense realization theorem** · theorem · **partial**

The normed continuous-surjection density/range theorem is proved. General Hausdorff TVS and arbitrary fibre aggregation remain.

Source: `editable/traditional/04_transport.tex:305-318`.

Existing contract rows: 29.

Declarations: `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.dense_operatorHull_image`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.map_packetRange_eq`.

### 100 · PSC-I-T-QUOTIENT-TOPOLOGY-COMPLETION
**Quotient topology and completed realization** · theorem · **partial**

Dense isometric completion is proved in normed spaces. General quotient topology identification and locally convex realization remain.

Source: `editable/traditional/04_transport.tex:333-344`.

Existing contract rows: 1, 29.

Declarations: `Komorebi.SeedRankBasics.oneSeedQuotientEquivRange`, `Komorebi.SeedRankBasics.oneSeedQuotientEquivRange_apply_mk`, `Komorebi.SeedRankBasics.generates_singleton_iff_surjective`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_intertwines`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_unique`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.dense_operatorHull_image`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.map_packetRange_eq`.

### 101 · PSC-I-B-TOPOLOGICAL-QUOTIENT
**Continuous surjections and quotient topology** · boundary · **scope_boundary**

The quotient-map requirement is preserved; no open-map theorem is inferred from continuity alone.

Source: `editable/traditional/04_transport.tex:352-355`.

### 102 · PSC-I-D-REALIZATION-FUNCTOR
**Realization functor and preservation profile** · definition · **documentary**

The declared preservation profile is metadata, not an instantiated Lean functor with all listed preservation proofs.

Source: `editable/traditional/04_transport.tex:382-397`.

### 103 · PSC-I-T-REALIZATION-EXPORT
**Equational realization principle** · theorem · **not_mapped**

Need formal typed expression/diagram transport for additive or linear functors and the claimed preserved constructions.

Source: `editable/traditional/04_transport.tex:400-403`.

### 104 · PSC-I-P-REALIZATION-EXPORT
**Realization export principle** · proposition · **not_mapped**

Proof-profile transport remains a semantic theorem target, not a blanket consequence of matching names.

Source: `editable/traditional/04_transport.tex:432-435`.

### 105 · PSC-I-D-SEMANTIC-REALIZATION
**Semantic realization criterion** · definition · **documentary**

A methodology and scope checklist, not automatic formal certification.

Source: `editable/traditional/04_transport.tex:443-453`.

### 106 · PSC-I-ALG-EXAMPLE-SLOTS
**Reserved example slots** · definition · **documentary**

Example slots are editorial. Existing examples and algorithm specifications remain outside the 69 proved-record denominator.

Source: `editable/traditional/04_transport.tex:470-480`.

Existing contract rows: 30, 31, 32, 33, 34, 35.

Declarations: `Komorebi.PacketNaturalityCompletion.TypedQuiver.typed_reachability_certificate`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.BilateralShiftRepresentation.concretePower_apply`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.concreteBilateralShift_topologicallyCyclic`, `KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.concreteBilateralShift_seedCardinality_isLeast`, `Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity`, `Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity_of_distinct`, `Komorebi.SingleOperatorGraph.operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast`, `Komorebi.SingleOperatorGraph.operatorAlgebra_seedRank_eq_of_seedNumber_isLeast`, `Komorebi.SingleOperatorGraph.path_endpoint_seedNumber_isLeast_one`, `Komorebi.SingleOperatorGraph.complex_cycle_seedNumber_isLeast_two`, `Komorebi.FiniteAlgorithms.orbitHull_algorithm_terminates_and_correct`, `Komorebi.FiniteAlgorithms.orbitClosureIter_eq_orbitHull_of_stop`, `Komorebi.FiniteAlgorithms.transferBlockTable`, `Komorebi.FiniteAlgorithms.assembleTransferBlockTable`, `Komorebi.FiniteAlgorithms.transferBlock_algorithm_correct`, `Komorebi.FiniteAlgorithms.transferGraph_iff_block_ne_zero`, `Komorebi.FiniteAlgorithms.exactGraphSeedRank`, `Komorebi.FiniteAlgorithms.exactGraphSeedRank_isLeast`.

### 107 · PSC-I-EXPORT
**Paper I export object** · definition · **documentary**

An export catalogue, not one additional kernel theorem or a completed formal package object.

Source: `editable/traditional/04_transport.tex:483-503`.

### 108 · PSC-I-B-FINAL-CLAIM-BOUNDARY
**Exact limits of Paper I** · boundary · **scope_boundary**

No discoverability, conditioning, identifiability or later-paper existence claim follows automatically from finite packet identities.

Source: `editable/traditional/04_transport.tex:532-535`.
