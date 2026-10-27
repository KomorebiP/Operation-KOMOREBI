# Original tagged contour integral comparison

**Verdict: proved as written.** Every continuous bounded-variation original complex path on[0,1], with a Banach-valued integrand continuous on its trace, has a genuine all-tagged-partitions Riemann-Stieltjes limit equal to the velocity integral of its constructed Lipschitz arclength representative. The finite-family wrapper counts every curve occurrence.

This is an independent raw-source semantic review, separate from compiler success. The exact revision and dependency hashes are in RS_SEMANTIC_AUDIT.json. Final source freeze confirmed. The separate geometric norm-bound corollary was reviewed in RECTIFIABLE_DEFECT_AUDIT.json.

## Exact objects and quantifiers

`taggedSum` uses the original complex increments f(p(j+1))-f(pj) and H(f(qj)). `HasTaggedContourIntegral` quantifies over every natural n and every real endpoint/tag sequence with p monotone on0..n, exact endpoints, qj in the actual closed subinterval, and every interval width below one positive delta. It is a mesh epsilon-delta definition over all tagged partitions, rather than a selected sequence of partitions.

The fine-partition lemma proves nonvacuity for every positive tolerance by equispaced subdivisions. The uniqueness theorem uses one common fine partition and two epsilon/2 estimates. Thus the choice-defined integral is forced to equal the proved limit, and its undefined-case zero convention does not supply any existence premise.

## Critical implication

Coordinatewise absolutely-continuous FTC identifies actual path increments with integrals of their actual coordinate velocity. The local error is the integral of velocity times the difference between the tagged integrand value and the pointwise integrand value. Summing adjacent intervals and bounding the norm gives speed integral times a common oscillation bound. Compact uniform continuity of H composed with f supplies this bound uniformly over every admissible partition and tag. The epsilon/(V+1) choice includes V=0.

For a continuous monotone reparameterization phi, each arbitrary source partition and its tags map to a valid target partition and tags. Uniform continuity of phi supplies the target mesh bound, and original path increments agree termwise with target increments. Non-strict monotonicity is sufficient: flat segments produce repeated partition points and zero increments. No derivative of phi, inverse of phi, or assumed contour/velocity equality is used.

For continuous BV f, the baseline raw source constructs its arclength representative G and continuous monotone cumulative variation map. If length L>0, phi=arcMap/L gives f=G composed with phi exactly. If L=0, the source proves f=G directly and never divides by L. The representative is Lipschitz, hence absolutely continuous, and has the original trace. Pulling back the preceding all-partitions limit proves the claimed original-path comparison.

## Edge cases and scope

Repeated partition points are admitted and contribute zero. The zero-interval case admits honest repeated partitions and yields zero integral. Original curve self-intersections are unrestricted. Finite family sums retain repeated curves as distinct Fin n indices; an empty family gives zero. Increasing orientation is preserved. Reversal invariance, discontinuous BV curves, Cauchy vanishing, canonical holomorphic calculus independence, and exact geometric-length/speed equality are outside this module.

No missing implication was found for the normalized claim. The cheapest final check is to bind the finished source hash to its strict compilation receipt and confirm any added corollary does not change these definitions.
