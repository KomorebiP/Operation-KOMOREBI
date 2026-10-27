# Paper I completion, Block 05: geometric multiplicity without diagonalizability

## Scope and result

Let k be an algebraically closed field, V a finite-dimensional k-vector space, and T an endomorphism. The new development proves

    seedRank_{k[T]}(V) = max_{a in spectrum(k,T)} dim_k ker(T - a I).

The natural-valued seedFinrank formula is proved separately from its cardinal-valued counterpart. The empty-spectrum maximum is zero. On a nonzero space the maximum is attained at an actual spectral value. No diagonalizability, self-adjointness, eigenbasis, Jordan basis, primary presentation, supplied multiplicity, or assumed seed-rank equality appears among the public theorem's inputs.

This is a classical theorem newly completed inside Paper I's actual operator and seed-rank definitions. It is not a claim that the classical formula was newly discovered. The proof does not first construct a Jordan normal form. It instead uses the literal intrinsic quotient already constructed in Block 04, a natural cokernel identification, and rank-nullity.

The mathematical modules are `PaperICompletion5.LinearPrimaryEigenspace`, `PaperICompletion5.GeometricSeedFormula`, and `PaperICompletion5.CyclicGeometricCriterion`. `PaperICompletion5.lean` is an import-only root. Verification scope and counts are recorded separately in `VERIFICATION.json`.

## 1. The polynomial-module quotient is the actual cokernel

The original vector space V carries the actual polynomial action p*x = p(T)x through `Module.AEval' T`. For any polynomial p, `polynomialCokernelMap T p` sends a vector in this polynomial module to its original vector's class in V/range(p(T)).

`polynomialCokernelMap_surjective` proves surjectivity by lifting an ordinary quotient representative. `polynomialCokernelMap_ker` proves the exact kernel is the restriction to k of the literal polynomial scalar-image submodule pV. Both directions of this equality are established. A surjectivity statement is not being substituted for a kernel computation.

The resulting `polynomialQuotientEquivCokernel` is a k-linear equivalence

    V/pV  ≃_k  V/range(p(T)).

`polynomialQuotientEquivCokernel_mk` records its action on representatives: the class of the actual vector is sent to the class of the same vector. This is not an equivalence selected merely because two dimensions are equal. The cokernel-map and representative constructions themselves do not need finite-dimensionality.

## 2. A linear primary residue field has base-field dimension one

For any a in k, the evaluation quotient k[t]/(t-a) is naturally isomorphic to k. `linearResidue_finrank` applies the pinned Mathlib evaluation-quotient algebra equivalence to prove its k-dimension is one.

The intrinsic multiplicity in Paper I is a dimension over the residue field, not over k. The scalar tower is therefore retained explicitly in the dimension argument. For p=t-a, the tower law gives

    dim_k Q = dim_k(k[t]/(t-a)) * dim_{k[t]/(t-a)} Q
            = dim_{k[t]/(t-a)} Q.

The compatible scalar actions are the canonical quotient actions. They are not arbitrary field actions installed to force this equality.

## 3. Intrinsic multiplicity equals actual eigenspace dimension

For a finite-dimensional endomorphism S, rank-nullity and the dimension formula for a quotient give

    dim_k(V/range(S)) = dim_k ker(S).

This is `finrank_cokernel_eq_finrank_kernel`. It does not assert a canonical isomorphism between kernel and cokernel. Only their dimensions are identified.

Now put S=T-aI. The proof composes the natural Block 04 primary-to-global quotient equivalence with the new polynomial cokernel equivalence and the residue-field dimension calculation. Polynomial evaluation identifies (t-a)(T) with T-aI. Thus

    mu_{t-a}(T) = dim_k ker(T-aI).

`intrinsicMultiplicity_X_sub_C_eq_eigenspace` proves this over an arbitrary field. Algebraic closure is not needed for a particular linear factor. Finite-dimensionality is needed for the dimension comparison. No diagonalizability assumption is used at any point.

## 4. The maximum is defined from eigenspaces, not from seed rank

`geometricMultiplicityValues T` is the set of dimensions of the actual eigenspaces as a ranges over k. `geometricSeedMaximum T` is the natural-number supremum of this set. Neither definition contains seed rank, a primary presentation, or an assumed equality with a desired answer.

The set is nonempty even when V is zero, because k contains zero. Its values are bounded using the already-proved intrinsic seed formula. Natural-number boundedness gives an attained maximum.

When k is algebraically closed, `monic_irreducible_eq_X_sub_C` proves that every monic irreducible is t-a for some a. The intrinsic-primary multiplicity value set and the geometric value set are therefore equal. This converts Block 04's presentation-free intrinsic maximum into the geometric maximum.

The public natural and cardinal rank formulas are

- `operator_seedFinrank_eq_geometricSeedMaximum`
- `operator_seedRank_eq_geometricSeedMaximum`.

No primary decomposition is supplied by the caller. The proof uses the previously proved intrinsic theorem rather than rebuilding or assuming its construction.

## 5. The displayed maximum uses the actual spectrum

The manuscript's formula is indexed by Spec(T), not all elements of k. `spectralMultiplicityValues` therefore includes a scalar only with a proof that it belongs to the actual algebra spectrum `spectrum k T`.

For a finite-dimensional operator, a scalar outside the spectrum has zero eigenspace dimension. Removing those off-spectrum zeros does not change the natural supremum. `geometricSeedMaximum_eq_spectralSeedMaximum` proves this even over a field that is not algebraically closed. Algebraic closure is needed for the equality of these maxima with the seed rank, not for deleting zero contributions.

The exact manuscript-facing theorems are

- `operator_seedFinrank_eq_spectralSeedMaximum`
- `operator_seedRank_eq_spectralSeedMaximum`.

On the zero space the spectral set can be empty, and its natural supremum is zero. On a nonzero space over an algebraically closed field the geometric maximum is positive. A scalar attaining that positive value must be spectral. `spectralSeedMaximum_attained` supplies the actual spectral witness.

## 6. Cyclicity and multiplicity one

For a nonzero finite-dimensional space over an algebraically closed field, the following equivalence is now proved from actual objects:

    T has a cyclic vector
      iff every a in spectrum(k,T) has dim_k ker(T-aI) = 1.

`hasCyclicVector_iff_all_spectral_multiplicities_one` combines the new maximum theorem with Block 02's actual cyclic/minpoly and seed-rank-one results. `minpoly_eq_charpoly_iff_all_spectral_multiplicities_one` gives the equivalent polynomial equality criterion.

The nonzero-space guard is retained when cyclicity is expressed as seed rank one. The zero space has seed rank zero although its at-most-one-generator cyclicity predicate holds. The negative-control suite rejects an attempt to use the nonzero-space theorem without a Nontrivial instance.

These are results over a field that is already algebraically closed. They are not yet a theorem about scalar extension of an arbitrary-base-field operator to an algebraic closure.

## 7. An actual one-factor presentation

For any field, `cyclicMinpolyQuotientEquiv` constructs

    Module.AEval' T ≃_{k[t]} k[t]/(minpoly_k(T))

from an actual cyclic vector and surjectivity of its polynomial orbit map. It uses the already-proved exact orbit-map annihilator identification and the orbit quotient equivalence. It does not receive a one-factor count certificate.

`hasCyclicVector_iff_minpoly_quotient_presentation` proves the converse as well. Given an actual polynomial-module equivalence, lift the class of 1 to V. Every quotient element has a polynomial representative, so that lifted vector has a surjective orbit map. The theorem is a mathematical existence statement, not a verified procedure for calculating rational canonical form.

The full six-way cyclic criterion in the manuscript remains partial. Formal scalar-extension preservation/descent and the exact assembly of its primary-component and rational-canonical clauses are still separately tracked. The new one-factor module presentation is not silently renamed a completed executable companion-matrix construction.

## 8. Exact boundary tests

The new test module contains 23 theorem assertions.

A literal X-action on C[t]/(t^2) is proved to have vector-space dimension two, square zero, and be nonzero. Its eigenspace at zero has dimension one and its seed rank maximum is one. The test proves that it has no eigenbasis indexed by Fin 2. This exercises a non-diagonalizable operator, not a diagonal example accidentally used to support the general theorem.

Two primary chains at zero, of lengths one and two, have geometric multiplicity and seed count two. Chain length is not incorrectly counted as the number of generators.

The rational primary module Q[t]/((t^2+1)^2) supplies a genuine guard against dropping algebraic closure. It has seed rank one but every rational eigenspace is zero, so its rational geometric maximum is zero. The test proves the inequality of seed rank and that maximum.

Other assertions check the zero space, the exact scalar-image kernel, literal quotient representative behavior, and the actual one-factor presentation. Tests are Lean theorems, not numerical experiments. The audit's separate negative fixtures deliberately contain invalid applications or proof placeholders; those fixtures are not production sources.

## 9. Remaining work and trust boundary

The geometric-multiplicity corollary is now mapped at its full recorded finite-dimensional algebraically closed scope. The scalar-extension clause of the larger cyclic criterion remains. So do the separately tracked nonsplit semisimple, module-top/Nakayama, expanded packet/functorial/topological, and executable algorithm obligations. Papers II–XII have not been rerun in this sweep.

The constructions are noncomputable. There is no eigenvalue-finding algorithm, symbolic factorization implementation, numeric stability or performance claim in this block. Same-kernel replay and cached dependency reuse are distinguished from an independent verifier and a full dependency rebuild in the verification report.
