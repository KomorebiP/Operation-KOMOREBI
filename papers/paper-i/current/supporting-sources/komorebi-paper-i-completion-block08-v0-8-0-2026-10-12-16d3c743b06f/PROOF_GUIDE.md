# Paper I completion, Block 08: nonsplit semisimple seed rank

## Scope

Let A be a semisimple Artinian ring and M a finitely generated left A-module. A division ring in this guide is not assumed commutative. The development constructs a finite family of division rings D_i, positive matrix sizes d_i, multiplicities m_i, an actual ring isomorphism

    A ≃ product_i M_(d_i)(D_i),

and a compatible semilinear module isomorphism

    M ≃ direct_sum_i (D_i^(d_i))^(m_i).

For the canonical seed rank already used throughout Paper I, it proves

    seedRank_A(M) = max_i ceil(m_i / d_i).

The maximum is zero for an empty family. The public existence theorem constructs both presentations internally. No decomposition, generator family, multiplicity equality or rank conclusion is supplied by its caller. Separate transport theorems establish the same formula for any displayed compatible presentations.

The actual module top gives a stronger extension: for any left Artinian ring A and finitely generated M, the formula on M/JM over A/J computes seedRank_A(M). The finite-dimensional-algebra clause in the manuscript follows because finite dimension over a field supplies Artinianity internally.

These are classical mathematical statements completed inside the existing Komorebi objects. This block does not claim discovery of a new classical semisimple-module classification. The constructions are noncomputable mathematical objects, not a verified executable Wedderburn or normal-form algorithm.

## 1. A left matrix module is controlled by the left span of its rows

Fix a division ring D and positive d. Model m copies of the natural left M_d(D)-module by d-by-m matrices. The scalar action is literal LEFT matrix multiplication.

For r seed matrices V_j, the definition `DivisionRows.LeftGenerates` says that every target X admits coefficient matrices A_j with

    X = sum_j A_j V_j.

The companion `RowsSpan` predicate is the actual left-D submodule span of the rd row vectors. `leftGenerates_iff_rowsSpan` proves these predicates equivalent.

Forward, choose a target whose selected row is any prescribed y in D^m, and read that row from the generating expression. It writes y as a left-D combination of the seed rows. The hypothesis d > 0 is needed to select a row.

Reverse, choose row-span coefficients for every target row and assemble the coefficients into the matrices A_j. The proof establishes equality entry by entry. Coefficients stay on the left throughout; commutativity of D is never invoked.

The dimension bound for a spanning family over a division ring yields

    m ≤ r d.

For the reverse inequality, choose an embedding of the m coordinate positions into the rd available seed-row positions. Place a standard basis row in each selected position and zero in the unused positions. These rows span D^m, so the constructed seed matrices generate.

Consequently an r-element generating family exists exactly when m ≤ rd. The natural ceiling is proved to be the least such r. `DivisionBlock` identifies this minimum with the ORIGINAL `seedFinrank` and cardinal-valued `seedRank`, using actual submodule-generation predicates rather than introducing a replacement rank definition.

## 2. Different factors assemble by a maximum, not a sum

`DivisionProduct` permits a dependent family of division rings D_i. Different factors need not even have the same underlying type. Its product ring and multiplicity module use the literal componentwise actions.

A family generates the product module exactly when each coordinate family generates its own matrix block. To pass from coordinate expressions to a product expression, assemble each block's coefficient matrix into one element of the product algebra. This is genuine independent control between different ring factors.

Thus r seeds exist exactly when

    m_i ≤ r d_i   for every i.

The minimum is `maxCeilDiv d m`, defined from the multiplicities and matrix sizes, not from seed rank. Taking the finite supremum gives zero for an empty product. Absent module factors with m_i = 0 contribute zero.

This independence is not present between multiple copies of the same natural module under one shared M_d(D) action. Three copies of D^2 therefore need two seeds, even though two different ring factors can share the same seed index.

## 3. Natural modules, simplicity and the regular-module decomposition

For a nonzero x in D^d, choose a coordinate x_j ≠ 0. For any target y, the matrix whose j-th column has entries y_i / x_j and whose other columns vanish sends x to y. The order is y_i x_j^(-1), not x_j^(-1) y_i.

`natural_nonzero_generates` proves this statement and `natural_seedRank_eq_one` proves the canonical rank-one consequence for positive d. The product-factor natural module `Simple d i` is obtained by scalar restriction through the actual coordinate ring homomorphism. Its action is proved to select the i-th matrix factor. Other factors act by zero. Its simplicity follows from generation by every nonzero vector, rather than being assumed in its definition.

`regularColumnsEquiv` maps a regular algebra element a to its individual columns:

    (a_i)_(row,column) ↦ column ↦ row ↦ (a_i)_(row,column).

It is an actual left-A-linear equivalence. Its A-linearity is the ordinary identity saying that left multiplication acts separately on each column. It is NOT an assertion that transpose is a ring homomorphism, or that transpose reverses multiplication over a noncommutative coefficient ring.

`regularDirectSumEquiv` composes the column map with the finite-product/direct-sum equivalence, establishing the manuscript's regular multiplicities

    A ≃ direct_sum_i S_i^(d_i).

For general multiplicities, `columnsEquiv`, `singleColumnsEquiv`, `multiplicityDirectSumEquiv`, `naturalDirectSum_seedRank` and `directSum_seedRank` connect the rectangular-matrix, repeated-natural-module and actual finite-direct-sum formulations. All scalar actions are carried along these equivalences.

## 4. Compatible module decompositions are constructed, not assumed

Importing a ring decomposition does not alone identify arbitrary simple modules with its natural columns. `ProductPresentation` supplies this missing compatibility.

First, a simple module S over the product algebra embeds as a left ideal of its regular module, using the proved semisimple-module machinery. Compose that embedding with `regularColumnsEquiv`. A nonzero vector in S has a nonzero image and therefore a nonzero coordinate in some natural column. Projection onto that column gives a nonzero A-linear map

    S → S_i.

Both source and target are genuinely simple. Schur's lemma makes this map bijective, yielding `simple_equiv_natural`. No classification conclusion is stored as an input field.

A finitely generated module over a semisimple ring has an actual finite simple-summand decomposition. Apply the preceding construction to each summand. The resulting factor-index map assigns each summand to a natural factor. `regroupSimpleFactors` gives an explicit linear coordinate equivalence grouping summands by its fibres and replacing each finite fibre by `Fin` of its cardinality.

`exists_multiplicity_presentation` therefore constructs the required m_i and the actual product-module equivalence. The multiplicities count proved simple summands; they are not defined by an assumed seed-rank equality.

For a ring A isomorphic to the product, `exists_compatible_presentation` installs the transported module action through the inverse ring homomorphism, proves the identity map is semilinear for the given ring isomorphism, preserves finite generation, applies the product result and composes back. This preserves the exact supplied ring decomposition rather than choosing an unrelated second decomposition.

## 5. Abstract existence and the canonical formula

`SemisimpleFormula.exists_wedderburn_decomposition` integrates the pinned proved theorem

    IsSemisimpleRing.exists_ringEquiv_pi_matrix_divisionRing.

The source also integrates the actual finite simple-module decomposition theorem. These are proved dependencies in the pinned Mathlib, not new axioms. The local source ownership and transitive-axiom audit retains that distinction.

The public theorem

    SemisimpleExistence.exists_semisimple_seed_formula

starts with the ring, the module, semisimplicity and finite generation. It produces the division rings, positive sizes, multiplicities, ring isomorphism, compatible module isomorphism and the canonical rank equality. Its proof combines abstract ring existence, the new compatible module construction and the independently proved row-based formula.

The separate `semisimple_seedRank_of_decompositions` and natural-valued variant apply to any actual compatible displayed presentations. Thus a caller with their own presentation can use the same theorem without replacing it by a chosen one.

## 6. The literal radical quotient and the exact split corollary

Block 07 already proves

    seedRank_A(M) = seedRank_(A/J)(M/JM)

for finitely generated modules over arbitrary unital rings. That proof is reused without modification. For an Artinian ring, the radical quotient is semisimple. The new theorem constructs its compatible top decomposition and computes the original module's rank. For finite-dimensional algebras, the required Artinianity is derived from the field-dimension hypothesis.

The manuscript's split corollary displays a decomposition of the ORIGINAL A together with M/JM. This is slightly different from displaying A/J. The new development proves both formulations explicitly.

`seedRank_eq_radicalTop_restricted` shows that the literal quotient has the same generating number whether its action is viewed over A or A/J. It uses the actual quotient scalar map and a bijective semilinear identity map. `split_originalRing_top_seedRank` then matches the printed original-ring formulation. `split_radicalTop_seedRank` handles the quotient-ring formulation.

Neither split transport theorem needs algebraic closure once the displayed split decomposition is supplied. No assertion that every arbitrary division ring is a field is used. No executable procedure for splitting a given algebra is claimed.

## 7. Boundary suite

The new exact Lean assertions use the rational quaternion division ring H. They prove that H is genuinely noncommutative, that a reversed coefficient order fails, and that three and five copies of the natural M_2(H)-module require two and three seeds respectively. The direct-sum formulation and actual generator existence are tested separately from the cardinal formula.

A dependent two-factor family uses H in one factor and Q in the other. The tests verify maximum rather than sum, zero contribution of an absent factor, vanishing action of the wrong factor, literal regular-column entries, A-linearity and inverse identities. Empty products and zero multiplicities are covered.

A zero-size matrix example proves why d > 0 cannot be dropped: all 0-by-1 target matrices are trivial, so an empty seed family generates them although the unguarded row bound 1 ≤ 0 fails.

The public finite-algebra theorem is instantiated on the square-zero extension of H by H. Its rational finite-dimensionality is proved using the literal linear equivalence with H × H. The test supplies no Wedderburn or module-presentation certificate.

These are exact proof assertions and integration checks, not numerical experiments. Deliberately invalid source applications and injected forbidden axioms/placeholders are kept separately from production proofs. The accepted verification report gives exact counts and observed outcomes.

## 8. Remaining scope and verification boundary

The nonsplit semisimple block, compatible abstract decomposition integration and radical-top formula are complete at their recorded scopes. This does not finish every record in the expanded 108-record monograph. Other packet, functorial, topological and executable-algorithm obligations remain in the coverage map. Papers II–XII have not been rerun in this sweep.

The new mathematical modules are freshly compiled. Predecessor sources and compiled objects are authenticated, not freshly recompiled in this block. The complete logical project closure is rechecked with Lean's own kernel from an upstream-only starting environment, with exact name-set matching against ownership audits. Seven inherited generated partial runtime helpers are separately classified and are not described as proof-replayed logical declarations. Mathlib's authenticated cache is reused, not rebuilt or fully replayed. This is not an independently implemented verifier.
