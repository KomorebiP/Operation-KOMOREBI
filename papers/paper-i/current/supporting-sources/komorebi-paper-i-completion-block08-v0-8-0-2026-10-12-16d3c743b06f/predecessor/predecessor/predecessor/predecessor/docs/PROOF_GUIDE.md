# Paper I completion, Block 04: the intrinsic primary quotient

## The statement being completed

Let k be a field, V a finite-dimensional k-vector space and T an endomorphism. Regard V as the actual polynomial module with p acting by p(T). For each monic irreducible p, define

    X_p = {x in V : p(T)^n x = 0 for some n},
    mu_p(T) = dim_{k[t]/(p)} X_p / p(T)X_p.

The new development identifies each mu_p(T) with its elementary-divisor count and proves

    seedRank_{k[T]}(V) = max_p mu_p(T).

The maximum is over all monic irreducibles, not just the labels in a caller-supplied decomposition. Its finiteness and attainment are proved. No diagonalizability or splitting assumption is present.

The underlying formula is classical. This block completes its integration into Paper I's literal objects and definitions. It does not claim a new classical theorem or a completed formalization of the entire expanded monograph. Compiler acceptance is recorded separately in VERIFICATION.json.

## 1. The actual scalar-image quotient

`ScalarQuotient M p` is exactly

    M / (p • top),

where `p • top` is the submodule of actual scalar multiples p x. It is not an abstract quotient type equipped with an assumed dimension. `mem_scalarImage_iff` proves its membership predicate is existence of a preimage under multiplication by p.

The quotient has the canonical R/(p)-module structure. A generic lemma, `scalarQuotientEquiv`, constructs an R/(p)-linear equivalence from an R-linear map f with proved surjectivity and proved kernel pM. The construction descends through the actual quotient by the actual kernel. Its residue-ring linearity is checked by lifting each scalar class to R. The representative theorem states that [x] maps to f(x).

Thus the later dimension comparisons are over the residue field, not merely over k or over R.

## 2. The full residue-map kernel

Consider a positive primary product

    M = product_i R/(q_i^{e_i}),

with each q_i irreducible and e_i > 0, over a principal ideal domain. Fix an irreducible p. The full residue map keeps those coordinates with (q_i) = (p), reducing each to R/(p).

For a matching coordinate, its residue class is zero exactly when it is a multiple of p. This follows by lifting to R and using membership in the principal ideal (p).

For a nonmatching coordinate, p and q_i^{e_i} are coprime. A Bezout identity makes multiplication by p surjective on R/(q_i^{e_i}). Consequently, every discarded coordinate is already in the scalar image pM.

Both cases are essential. Ignoring the discarded coordinates would not prove the kernel of the full map. `primaryResidueMap_ker` proves the exact equality

    ker(residue map) = pM.

The inherited surjectivity proof is then combined with this new kernel proof to construct `primaryProductQuotientEquiv`:

    M/pM ≃_{R/(p)} (R/(p))^{number of matching factors}.

There is no assumed kernel certificate in the public product theorem. An absent label gives the zero-dimensional empty fibre.

## 3. The intrinsic primary component

`primarySubmodule M p` has carrier exactly

    {x : exists n, p^n x = 0}.

Closure under addition uses the maximum of two killing exponents. Closure under scalar multiplication uses commutativity. `primarySubmodule_eq_idealPrimary` identifies this object with Mathlib's primary component for the principal ideal (p), rather than introducing a competing unexplained notion.

For the actual polynomial module `Module.AEval' T`, `operator_primary_membership` proves that this is precisely the p(T)-annihilation condition on the original vector space. `operator_scalarImage_membership` similarly identifies scalar image with the literal image of p(T).

## 4. Exactness of the intrinsic inclusion

The map `primaryToGlobal` is the inclusion X_p -> M followed by the quotient M -> M/pM.

Its kernel is pX_p for every module over a commutative ring. No Artinian or finite-dimensional assumption is needed for this kernel equality.

Indeed, suppose x is primary and x = py in M. If p^n x = 0, then p^{n+1}y = 0, so y is primary too. This proves X_p intersect pM = pX_p and gives the exact kernel equality in the primary subtype.

This is stronger than merely showing that pX_p is contained in the kernel. Both directions are formalized in `primaryToGlobal_ker`.

## 5. Surjectivity from stabilized images

Surjectivity requires a real finiteness hypothesis. For an Artinian R-module M, the descending chain of images of multiplication by p stabilizes. Choose n with

    image(p^n) = image(p^{n+1}).

For any x in M, this equality supplies y with

    p^n x = p^{n+1} y.

The vector x - py is killed by p^n and represents the same class as x modulo pM. Every global quotient class therefore has a primary representative.

The exact kernel and this surjectivity produce the natural residue-ring-linear equivalence

    X_p/pX_p ≃_{R/(p)} M/pM.

`primaryQuotientEquivGlobal_mk` records its action on representatives: [x] maps to [x]. The equivalence is induced by inclusion, not an arbitrary bijection between equal-dimensional vector spaces.

For finite-dimensional operators, the polynomial module is Artinian because the underlying k-vector space is Artinian and the action is compatible. This hypothesis is discharged internally in `operatorPrimaryQuotientEquiv`.

## 6. Grouped factors really are X_p

A primary decomposition of V does not, by itself, justify calling a selected product the intrinsic primary submodule. `primaryProduct_mem_iff` proves the needed identification.

In a coordinate labelled by a different irreducible, being killed by a power of p forces that coordinate to vanish, by a Bezout identity. In a matching coordinate, an appropriate power of p kills the whole factor. Finitely many matching coordinates share a common killing exponent, taken as a finite maximum.

The intrinsic component is therefore exactly the vectors supported on the matching coordinates. Restriction to those coordinates, with zero-extension as inverse, yields `groupedPrimaryEquiv`. Restricting any actual module equivalence to primary submodules yields `primaryCongr`.

Their composition, `operatorPrimaryComponentEquiv`, proves that the grouped elementary divisors form an actual decomposition of the literal X_p. This addresses the printed theorem's "moreover" clause, not only its numerical maximum.

The additional theorem `intrinsicMultiplicity_eq_card_of_component_decomposition` counts the summands in any supplied positive p-primary decomposition of X_p, including one not obtained by grouping a chosen decomposition of V. It assumes the decomposition, not the desired count. Existence is separately supplied by the constructed grouped decomposition.

## 7. Each intrinsic multiplicity, not just the maximum

For any actual positive primary presentation D of T, compose

    X_p/pX_p -> V/pV -> product_i R/(q_i^{e_i}) modulo p
               -> selected residue fibre.

Every arrow is a proved R/(p)-linear equivalence. When p is irreducible, R/(p) is a field. The selected residue fibre has dimension equal to its number of coordinates. Hence

    mu_p(T) = #{i : (q_i) = (p)}.

`primary_fiber_presentation_invariant` compares this same intrinsic dimension with two arbitrary actual presentations. This proves invariance of every individual primary multiplicity, strengthening Block 03's invariance of the maximum alone.

Associated irreducibles give the same principal ideal and therefore the same intrinsic multiplicity. Labels absent from a presentation have zero intrinsic dimension.

## 8. The exact printed maximum

`monicPrimaryMultiplicityValues T` is the set of values mu_p(T) for all monic irreducible p. It does not mention a primary presentation or seed rank in its definition. The set is nonempty, with p = t always available, even on the zero space.

Every value is bounded by the canonical seed number, using the now-proved individual fibre identification and the Block 03 primary-count formula. Thus this set of natural numbers is bounded and has an attained maximum. `intrinsicSeedMaximum_attained` proves that attainment.

To obtain equality with seed rank, normalize each irreducible in an actual primary presentation to a monic associate. Its intrinsic multiplicity is unchanged. This puts every primary count into the presentation-free value set. The two inequalities now give

    seedFinrank(operatorAlgebra T, V) = intrinsicSeedMaximum T.

A separate theorem gives the cardinal-valued `seedRank` equality. The public operator theorem takes T and finite-dimensionality, not a decomposition or an assumed seed-number identity. It internally uses the proved existence result from Block 03.

## 9. Boundary cases and limits

The exact regression suite uses p = t^2 + 1 over Q. Repeated primary chains have residue-field dimension two, whereas a single squared primary block has dimension one. The exponent and the degree of p are not additional generator multiplicities. The suite also checks absent labels, associated irreducibles, chosen-versus-explicit presentations, zero-dimensional spaces, the exact kernel and representative behavior.

The free module Q[t] gives a genuine limit: its t-primary component is zero, but Q[t]/tQ[t] is nonzero. The inclusion cannot be surjective on the quotient. The suite proves this failure, ensuring that the Artinian hypothesis in the global bridge is mathematically meaningful rather than decorative.

All constructions are noncomputable. This block does not implement factorization, an invariant-factor algorithm, an eigensolver or extraction/performance guarantees. The arbitrary non-diagonalizable eigenspace formula over an algebraically closed field and the scalar-extension clause of the larger cyclic criterion remain separate work.
