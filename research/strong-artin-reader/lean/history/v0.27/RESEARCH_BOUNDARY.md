# v0.27 research boundary

## Proven without a vanishing assumption

If a representation factors continuously through a finite quotient whose order is a unit in the upper square-zero coefficient ring, it has a continuous lift through the same quotient. Taking the quotient to be the actual residual image yields equality of the old and new kernels. Compactness of the source and discreteness of the residual coefficient ring ensure that this residual image is finite.

This is substantive obstruction vanishing derived by averaging, not a theorem assuming that H2 or the distinguished class vanishes. Historical novelty is not claimed.

For a prescribed representation of a subgroup of the same finite quotient, order invertibility for both that finite group and subgroup gives a lift preserving the prescription. The proof first averages the absolute two-cocycle, then adjusts its primitive using degree-one averaging on the subgroup.

## Exact continuous criteria in general

For discrete coefficient rings and a topological-group source, continuous provisional sections, continuous kernel actions, continuous defect cocycles, and a degree-two continuous inhomogeneous quotient are constructed.

The original representation lifts continuously iff its distinguished continuous class is zero. The fixed-subgroup version requires a continuous primitive vanishing on that subgroup. A continuous provisional section respecting any given continuous subgroup lift is constructed when the subgroup is clopen, in particular open.

## Important limits

1. ContinuousH2 is the explicit continuous inhomogeneous quotient using Mathlib's actual cocycle equation and differential. No formal equivalence to the separate homogeneous `continuousCohomology 2` API, derived-invariant functor, or Selmer complex is proved.
2. The source is NOT assigned the discrete topology in the main theorems. One discrete-source comparison is a sanity specialization only. The positive product-source example is proved compact and nondiscrete.
3. Coefficients for the obstruction construction are discrete. General non-discrete p-adic coefficient modules, topological sections there, and inverse-limit comparison require further arguments.
4. Provisional sections are chosen from the residual unit group. They are not representation lifts. The obstruction measures exactly their multiplicativity failure.
5. The order-invertible theorem does not apply when the actual finite residual-image order is noninvertible upstairs. No claim of covering the difficult defining-characteristic sector is made.
6. General global H2_cont need not vanish even in the finite-image sector: the theorem proves that the distinguished representation-lifting class vanishes by factoring through the finite image. It does not prove every global two-cocycle is a coboundary.
7. Prescribed-subgroup vanishing requires the prescription to factor through the displayed finite subgroup and the stated order hypotheses. Absolute vanishing does not suffice for arbitrary prescriptions; the negative control persists.
8. A clopen subgroup has an explicit relative criterion. General closed nonopen decomposition groups, multiple local conditions, and preservation up to conjugacy/gauge are not supplied by that criterion.
9. No arithmetic local Tate duality, Chebotarev instantiation, cotangent/Selmer comparison, or arithmetic auxiliary-prime descent is proved.
10. No nonzero automorphic carrier, automorphic support, or Strong Artin conclusion is obtained.
11. A square-zero step is not by itself a compatible inverse-limit theorem. All required local conditions must continue to hold in any iteration.
12. The theorem does not infer automorphy from the existence of a continuous representation lift. Those are separate constructions.

## Next meaningful target

For a precisely specified arithmetic representation, construct the correct continuous relative/Selmer obstruction with its actual local conditions and prove vanishing or produce a definite nonvanishing obstruction. Do not replace this by an unconstrained absolute H2 theorem or by arbitrary augmented equation variables.

An internal alternative with a different scope is a compatible finite-tower lifting theorem in the order-invertible sector, preserving the same quotient at every stage. That would be useful but would not address the wild locally constrained case or automorphic occurrence.

## Evidence boundary

Fresh source replay covers the 10 unchanged direct dependencies and 11 new modules, plus an all-named-constant axiom audit. The pinned Mathlib compiled cache is trusted and reused. This is self-review plus Lean checking, not an independent specialist referee report or a complete historical branch reconciliation.
