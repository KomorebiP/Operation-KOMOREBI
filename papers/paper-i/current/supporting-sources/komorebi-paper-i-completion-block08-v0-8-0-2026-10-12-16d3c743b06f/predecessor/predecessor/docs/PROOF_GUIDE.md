# Paper I completion, Block 06: scalar extension and the six-way cyclic criterion

## Scope

Let k be a field, V a finite-dimensional k-vector space, and T an actual k-linear endomorphism of V. For an extension field K with its specified k-algebra structure, write

    T_K = T.baseChange K : End_K(K ⊗_k V).

The operator on the right is the literal tensor-product endomorphism. It is not an unrelated operator over K chosen to have matching invariants. The extension need not be finite, algebraic, or separable for the minimal-polynomial and cyclicity preservation theorems. Algebraic closure is required only for the geometric clause.

The main result assembles all six printed cyclicity conditions for nonzero V. The scalar-extension statements themselves include the zero space. These are classical mathematical results newly connected to the paper's actual objects and seed-rank definitions, not claims of new classical discoveries.

The mathematical source is in four modules under `source/extension/PaperICompletion6`. The import-only root is `PaperICompletion6.lean`. Verification results are governed by `VERIFICATION.json` and the hashed accepted-run receipt, not by this explanatory guide.

## 1. The full endomorphism space commutes with base change

The first bridge is stronger than injectivity of T ↦ T_K. It identifies

    K ⊗_k End_k(V) ≃_K End_K(K ⊗_k V)

with the actual base-change map on pure tensors. Finite-dimensionality is used here.

`tensor_endHom_eq_baseChange` proves that the map furnished by the tensor universal property is literally `LinearMap.baseChangeHom`. `isBaseChange_endomorphisms` applies the pinned Mathlib theorem for endomorphisms under base change to that identified map.

`linearIndependent_baseChange` then proves that any k-linearly independent family of operators becomes K-linearly independent after extending those actual operators. The proof first extends the family into the tensor product, using flatness of the field extension, and then maps it through the constructed equivalence. It does not infer K-linear independence from k-linear injectivity alone.

In particular, if d is the degree of the original minimal polynomial, the operators

    1, T_K, ..., T_K^(d-1)

are K-linearly independent. This is `linearIndependent_baseChange_powers`.

## 2. The minimal polynomial is preserved exactly

`aeval_map_baseChange` proves the evaluation identity

    (map_{k→K} p)(T_K) = (p(T))_K

for every polynomial p. This identity itself does not require finite-dimensionality.

Applying it to the original minimal polynomial shows that its coefficientwise image annihilates T_K. Its image remains monic. The preceding power-independence result rules out an annihilator of smaller degree over K. The pinned minimal-polynomial characterization from a monic annihilator and independent lower powers therefore gives

    minpoly_K(T_K) = map_{k→K}(minpoly_k(T)).

This is `minpoly_baseChange`. `minpoly_natDegree_baseChange` proves the exact degree equality.

The proof does not assume minimal-polynomial preservation, a supplied normal form, or descent of cyclicity. In particular, it does not try to descend the coordinates of an arbitrarily chosen cyclic vector over K. Such a vector need not itself lie in the original vector space. Existence downstairs is recovered from the invariant polynomial equality instead.

## 3. Cyclicity is preserved and reflected

The already proved characteristic-polynomial base-change theorem gives

    charpoly_K(T_K) = map_{k→K}(charpoly_k(T)).

The coefficient map is injective because k and K are fields and the algebra map is unital. Thus

    minpoly_K(T_K) = charpoly_K(T_K)
      iff minpoly_k(T) = charpoly_k(T).

This is `minpoly_eq_charpoly_baseChange_iff`.

Block 02 already proved cyclicity equivalent to minimal polynomial equalling characteristic polynomial for arbitrary finite-dimensional endomorphisms, without requiring a supplied polynomial bridge. Composing that result on both sides yields

    HasCyclicVector(T_K) iff HasCyclicVector(T).

This is `hasCyclicVector_baseChange_iff`. It includes zero spaces, where the at-most-one-generator cyclicity predicate holds although the canonical seed rank is zero.

`baseChange_nontrivial` separately supplies nontriviality of the actual tensor space from nontriviality of V. This permits the nonzero-space geometric criterion of Block 05 to be applied with all its hypotheses discharged.

When K is algebraically closed, `hasCyclicVector_iff_extended_spectral_multiplicities_one` proves

    HasCyclicVector(T)
      iff every a in spectrum_K(T_K) has dim_K ker(T_K - aI) = 1.

The spectrum and eigenspaces are those of the actual tensor-product operator. This closes the scalar-extension distinction left explicitly open in Block 05.

## 4. The actual intrinsic primary components are cyclic

The next module links the original orbit predicate to the literal polynomial-module generator predicate:

    HasCyclicVector(T) iff Cyclic_{k[t]}(Module.AEval' T).

This is `hasCyclicVector_iff_polynomialModule_cyclic`. The polynomial action is still p·v = p(T)v.

A submodule of a cyclic module over k[t] is cyclic. The formal proof takes the preimage of the submodule under the surjective orbit map k[t] → V. That preimage is principal because k[t] is a principal ideal domain. Its generator maps to a generator of the original submodule. `submodule_cyclic_of_hasCyclicVector` proves this for every actual polynomial submodule, without a finite-dimensionality requirement.

In particular, `primary_cyclic_of_hasCyclicVector` proves cyclicity of the literal intrinsic primary component X_p. No isomorphic surrogate is silently substituted for X_p.

For the converse, a cyclic X_p has a cyclic quotient X_p/pX_p. The actual quotient map is surjective, and the quotient carries its canonical k[t]/(p) scalar action. The residue-field dimension lower-bound theorem from Block 03 gives

    μ_p(T) = dim_{k[t]/(p)}(X_p/pX_p) ≤ 1.

This is `intrinsicMultiplicity_le_one_of_primary_cyclic`. The proof does not use base-field dimension in place of residue-field dimension.

When every nonzero primary component is cyclic, zero components are handled explicitly as subsingleton cyclic modules. Every intrinsic multiplicity is therefore at most one. Block 04's unconditional intrinsic maximum formula gives seed rank at most one. Since V is nonzero, the canonical seed rank cannot be zero. It equals one, hence T is cyclic.

`hasCyclicVector_iff_nonzero_primary_cyclic` is the resulting exact primary-component clause.

## 5. One invariant factor means an actual presentation and companion basis

`HasOneInvariantFactor T` means that there is a monic positive-degree polynomial p and an actual k[t]-linear equivalence

    Module.AEval' T ≃_{k[t]} k[t]/(p).

It is not a supplied numerical count, a predicate defined to be cyclicity, or a requested conclusion stored in a certificate.

For any such monic presentation, `factor_eq_minpoly` proves p = minpoly_k(T). The proof compares the annihilator of the actual operator module with the annihilator of the quotient, then uses monicity to identify the generators of the equal principal ideals.

The forward cyclicity implication uses the actual minpoly-quotient equivalence proved in Block 05. Nontriviality gives positive degree. Conversely, a one-factor presentation has a generator, giving a cyclic vector for T. This proves `hasCyclicVector_iff_oneInvariantFactor`.

The development additionally realizes the matrix form, rather than stopping at the presentation:

* `quotientVectorEquiv` forgets only polynomial scalars and gives a k-linear equivalence from the quotient algebra to V.
* `quotientVectorEquiv_intertwines` proves that multiplication by the quotient class of t corresponds to the original operator T.
* `quotientCompanionBasis` transports the genuine quotient power basis to V.
* `toMatrix_quotientCompanionBasis` proves that the matrix of T in this basis is literally `companionMatrix p`.

The matrix convention is

    C(p)_{i,j} = -p_i       when j+1 = deg(p),
                1          when i = j+1 and j+1 ≠ deg(p),
                0          otherwise.

Thus the last column consists of the negatives of the lower coefficients and the subdiagonal consists of ones. The empty degree-zero matrix is included in the generic definition. `exists_companion_basis_of_cyclic` supplies the basis for the minimal polynomial of a cyclic operator, including the zero-space empty-basis convention.

Finally, `cyclic_iff_invariantFactor_count_one` proves that **any actual nonconstant divisibility-chain presentation** has exactly one factor iff T is cyclic. It uses Block 03's proved invariant-factor count, not an assumed equality of the count with seed rank. This connects the one-factor existence formulation to the invariant-factor count in a rational canonical presentation.

No executable rational-canonical algorithm, factorization routine, or full sorted invariant-factor construction for arbitrary noncyclic operators is claimed here.

## 6. The full printed six-way statement

For nonzero finite-dimensional V, `cyclic_six_way` proves `List.TFAE` for:

1. T has a cyclic vector.
2. The canonical cardinal-valued seed rank over the actual operator algebra k[T] is one.
3. Every nonzero intrinsic p-primary component, for each irreducible p, is cyclic as a k[t]-module.
4. There is an actual one-invariant-factor presentation as defined above.
5. The minimal polynomial equals the characteristic polynomial.
6. For the actual scalar extension to K, every spectral value has geometric multiplicity one.

The theorem is valid for any specified algebraically closed extension K. `cyclic_six_way_algebraicClosure` specializes it literally to Mathlib's `AlgebraicClosure k`, matching the publication.

The six-way theorem assembles previously established bridges and the new unconditional results. No decomposition, primary multiplicity certificate, spectral certificate, preservation certificate, or seed-number equality is a hypothesis of the final theorem.

The fourth clause is interpreted by an actual module decomposition with a constructed companion-matrix basis, not by a verified executable normal-form procedure. The conditional any-chain count theorem records the corresponding invariant-factor uniqueness-in-count statement needed here.

## 7. Boundary checks

The fresh regression suite uses the actual rational multiplication-by-t operator on

    V = k[t]/((t²+1)²),   k = Q.

In the test source, this module is represented as a one-coordinate product and explicitly identified with the single quotient by `squaredOneFactor` (`LinearEquiv.piUnique`). It proves that V has dimension four and its minimal polynomial is (t²+1)². After the actual extension to C, the mapped polynomial is again exactly (t²+1)² and its degree remains four. The extended operator is cyclic and every actual complex spectral value has geometric multiplicity one. The inherited rational eigenspace theorem gives dimension zero at every rational scalar. The combined assertion shows why a native rational geometric criterion cannot replace the extension clause.

The suite constructs a literal companion basis and checks the quotient intertwining equation for this operator. A separate entrywise assertion verifies the signs and orientation of the companion matrix of t²+1: [[0,-1],[1,0]].

Two repeated Jordan chains remain noncyclic after extension to an algebraic closure. A cyclic non-diagonalizable Jordan example has an actual companion basis. Zero-space minimal-polynomial compatibility and cyclicity preservation are tested, together with the fact that its canonical seed rank is not one. Characteristic-two instances of both minimal-polynomial preservation and cyclicity descent are also checked. These are type-correct exact Lean assertions, not numerical experiments or tests of an executable algorithm.

The negative fixtures deliberately omit finite-dimensionality, nontriviality, or algebraic closure, use a wrong companion sign, substitute the wrong cyclic operator for a repeated-chain operator, or contain a false equality or placeholder. Separate guard controls test imported forbidden axioms and placeholders outside the project namespaces. Their observed outcomes are recorded in the accepted-run receipt. Such intentionally invalid files are not production mathematics.

## 8. Verification boundary and next work

The current block freshly compiles its five new production modules against 37 authenticated unchanged predecessor source/object pairs. The acceptance workflow additionally inventories source-owned declarations, resolves public types and axioms, runs boundary and rejection controls, and serially replays all 42 production modules with Lean's official kernel. All of these acceptance operations completed successfully; the receipt records their observed results. No development object is accepted in place of a fresh new-module compilation.

The pinned Mathlib cache is reused, not rebuilt or fully replayed. Same-kernel replay is not an independent verifier. The publication-to-Lean correspondence is a reviewed semantic artifact, not a Lean interpretation of prose.

The coverage delta is exactly `PSC-I-C-CYCLIC-MATRIX`. Other records are not automatically upgraded merely because the operator classification is more complete. The next distinct target is the general, potentially noncommutative module-top/Nakayama theorem, followed by its local residue-division-ring corollary. Those results, the nonsplit semisimple development, packet/topological extensions, and executable algorithms are not supplied by this block. Papers II–XII have not been rerun in this sweep.
