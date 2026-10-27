# Deep mathematical audit

## Scope

This audit records the final internal review of *Residual Deformation Forests, Companion Systems, and Module Support*.

## 1. Residual fibers

The residual partition follows directly from the reduction map. Positive depth perturbations preserve reduction, so a vertical lift cannot cross between residual roots.

For a represented deformation problem, continuous maps into the complete coefficient ring are reconstructed from compatible maps into all finite quotients. The proof uses separatedness and completeness of the coefficient ring.

The finite branch theorem was checked in two forms. The first uses the stable cores of a Mittag Leffler inverse system. The second uses a finite branching tree and König's lemma. Individual nodes may die in both formulations.

## 2. Visibility and counting

The visibility partitions are nested. The separation depth

\[
w(i,j)=v_\varpi(a_i-a_j)+1
\]

satisfies the valuation form of the nonarchimedean law.

The weighted chart formula was checked coordinate by coordinate. The smooth and weighted counting series are geometric after the final visibility depth.

For \(x^e=0\), the exact valuation threshold is \(\lceil m/e\rceil\). The diagonal nilpotent count is the product of the one coordinate counts.

The normal crossing formula

\[
N_\times(m)=q^m+m(q-1)q^{m-1}
\]

was rederived by stratifying the first coordinate by valuation. Its rational series and branching exponent were checked independently. An earlier numerical count was corrected before the final build.

## 3. Cohomology and obstruction packets

Chain projectors that commute with the differential split cycles, boundaries, and cohomology. This gives exact tangent and obstruction packets under the standard deformation theoretic hypotheses.

The linear obstruction is the class of a defect in a cokernel. The solution set, when nonempty, is a coset of the correction kernel. Over a finite field this gives the exact child count.

The small extension statement is conditional on a complete obstruction theory. The article does not infer formal smoothness merely from a vector space called second cohomology.

## 4. Directed transport

The source component theorem is a finite graph theorem. Every generating set must meet each source strongly connected component, and one chosen vertex from each source component reaches the full condensation graph.

The theorem counts generation among residual roots and transports that are already known to exist. It does not construct a missing root or edge.

## 5. Companion forests

One place completion is an inverse limit theorem. A complete local object is obtained only when the inverse limit is identified with the declared complete local realization space.

The simultaneous theorem takes a product of nonempty compact local branch spaces. Every coordinate realizes the same declared algebraic spine. This is compatibility by shared Frobenius and local data, not a proof that the local spaces are nonempty.

The conditional completion theorem was tightened so vertical completion means an explicit bijection between complete local realizations and the finite inverse limit.

## 6. Finite Frobenius separation

Pairwise nonisomorphic absolutely irreducible constituents have linearly independent characters at one coefficient place. Chebotarev density allows the evaluation points to be chosen among unramified Frobenius classes. A finite subcollection gives a matrix of full column rank.

Strict compatibility places the selected traces in one coefficient field and makes the separator independent of the coefficient place.

The carrier theorem assumes a known compatible decomposition. It does not prove that an arbitrary representation lies in that carrier.

## 7. Fitting support

For a finite module over a Noetherian ring, localizing a finite presentation shows

\[
\Supp_R(M)=V(\Fitt_0^R(M)).
\]

The higher Fitting indexing was checked against the minimum number of local generators. The locus requiring at least \(r\) generators is

\[
V(\Fitt_{r-1}^R(M)).
\]

Full support is equivalent to equality of the radical of the annihilator with the nilradical. Faithfulness is sufficient but not necessary.

## 8. Base change

Arbitrary base change gives only a support inclusion. Flat base change gives equality because the localized flat local map is faithfully flat. Faithfully flat maps detect the zero module.

Noetherian adic completion is flat, so completed support is exactly the inverse image of the original support.

## 9. Finite occupancy

A central idempotent decomposes an Artinian module even when the algebra action is not semisimple.

The final manuscript restricts the trace test to characteristic zero. For an idempotent \(e\),

\[
\Tr_E(e)=\dim_E(eV)1_E,
\qquad
\rank_E(e)=\dim_E(eV).
\]

Thus nonzero trace detects occupancy in characteristic zero. This correction prevents the trace from vanishing merely because the packet dimension is divisible by the characteristic.

For commuting split semisimple operators, Lagrange projectors commute and their product is the exact joint eigenspace projector.

## 10. Infinite occupancy

The tail projections in \(\ell^2\) show that every finite packet can be nonzero while the infinite intersection is zero.

Nonvanishing survives under finite dimension, finite module length, compact nested intersections, or a nonempty Mittag Leffler stable core.

For a finite module over a complete Noetherian ring, a compatible finite packet branch reconstructs one module element. Excluding zero at every depth makes the reconstructed element nonzero.

## 11. Conditional assembly

The completion theorem has three logically separate layers.

1. Local inverse limits supply complete branches.
2. One common arithmetic spine identifies their Frobenius data.
3. Occupancy is supplied either by a known compatible carrier summand or by module support.

The two occupancy mechanisms require different data. The article does not claim a general equivalence between them.

## 12. Remaining boundaries

The article does not prove universal companion existence, universal global occupancy, automorphy, or unrestricted reciprocity. It also does not establish historical priority for the combined formalism.

## Audit conclusion

No unresolved internal contradiction or proof dependency was found after the final corrections. The highest risk results for outside review are the finite Frobenius separator in the stated compatible setting, the exact normal crossing series, the support based occupancy transition, and the conditional completion theorem.
