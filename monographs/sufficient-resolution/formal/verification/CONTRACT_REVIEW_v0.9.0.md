# Block-09 contract review

1. **Object identity:** `MetricObstruction.obstructionIsometry` uses the saved
   `obstructionEquivHarmonic` literally as its linear-equivalence field. The theorem
   `isometry_toLinearEquiv` is reflexive, so the algebraic correspondence is unchanged.
2. **Native norm:** no norm instance is defined in the new modules. The norm proof
   uses Mathlib's quotient representative infimum API and quotient projection bound.
   The inherited quotient can be only seminormed before closedness is supplied.
3. **Positive hypotheses:** R and K admit orthogonal projection. Neither finite
   dimension nor completeness is imposed when these projector hypotheses are given.
   The inner product preservation theorem has the native quotient's projection
   instance explicit; `compatibleRangeProjection` supplies it constructively in Prop.
4. **Minimum representative:** minimization is over compatible LOCAL representatives
   of a fixed class. This is different from block 08's global minimum source Bv.
5. **Intrinsic class:** c(v)=[P_K v] is nonexpansive and measures only obstruction.
   To characterize realization of arbitrary v one also requires delta(v)=0.
6. **Source integration:** the actual prior bounded recovery operator appears in
   residual/candidate identities. Complete/closed actual range remains required.
7. **Quantitative transport:** the map is the prior PresentationMap.obstructionMap,
   bounded from a whole-local-map certificate. No reverse map is inferred; a bounded
   left inverse is supplied when deriving the lower bound.
8. **Refinement:** quotient map is actual Submodule.mapQ, surjective, compositional,
   and contractive for the native norms. Energy identity fixes both K and the metric.
9. **Nonclosedness:** norm zero sees closure(R), algebraic zero sees R. The new theorem
   produces a nonzero zero-seminorm class for any nonclosed submodule. No bijective
   linear isometry to a genuine normed space can then exist. This is not a concrete
   infinite-dimensional operator construction and does not prohibit all noninjective
   norm-preserving maps from pseudometric spaces.
10. **Python:** known rational Euclidean models, capped dimensions, exact Fractions,
    seed 20260913. The Gram and ambient routes share matrix helpers. Arbitrary JSON
    parsing/elimination and the PSD helpers are not Lean-verified.
11. **Priority:** quotient-Hilbert and minimum-norm geometry are classical. The block
    certifies this implementation and its connections to saved Komorebi contracts,
    not historical novelty or a universal domain-independent existence theorem.
