# Rectifiable contour bridge: exact mathematical argument and formal contract

Status: the derivation below has now been implemented in three strictly compiled Lean modules. Matching source hashes and receipts are recorded in ANALYTIC_BRIDGE_CLOSEOUT.json. This does not close canonical holomorphic calculus.

Let f:[0,1]→ℂ be continuous with bounded variation and f(1)=f(0). Put L=Var(f), a(t)=Var(f;[0,t]), and choose the canonical arclength path g:[0,L]→ℂ, so f=g∘a, a is continuous monotone and onto, and g is 1-Lipschitz. The baseline already constructs these objects and proves these properties, with unit interval rescaling G(s)=g(Ls).

For a complex Banach space E and H continuous on the trace, define the classical contour integral as the limit of the genuine tagged Riemann–Stieltjes sums

S(f,H;P,τ)=Σ_j (f(t_{j+1})−f(t_j)) H(f(τ_j)),

where 0=t_0≤…≤t_n=1, τ_j∈[t_j,t_{j+1}], and max_j(t_{j+1}−t_j)→0. Repeated endpoints contribute zero and are allowed. This is the standard tagged RS definition, not a velocity integral renamed as classical contour integration.

For an absolutely continuous path G and its actual coordinate velocity v, the coordinatewise FTC gives G(b)−G(a)=∫_a^b v. Hence, on any interval [a,b] and any tag τ,

(G(b)−G(a)) H(G(τ)) − ∫_a^b v(s)H(G(s))ds
= ∫_a^b v(s)(H(G(τ))−H(G(s)))ds.

Consequently the norm is at most

osc(H∘G;[a,b]) × ∫_a^b ‖v(s)‖ds.

Summing over any ordered partition, the error is at most ω(mesh(P)) × ∫_0^1 ‖v‖, where ω is a modulus of uniform continuity of H∘G. Thus every tagged RS sum converges to the actual Bochner velocity integral. This argument requires only absolute continuity and integrable velocity, not continuity of the velocity.

To transfer from f to g, use the transformed partition a(t_j), with transformed tags a(τ_j). Every summand agrees exactly because f=g∘a. The transformed partition may have repeated points, but these summands vanish. Its endpoints are 0 and L. Uniform continuity of a ensures its mesh tends to zero when the original mesh does. The preceding error bound applied to g therefore proves that S(f,H;P,τ) converges to ∫_0^L g'(u)H(g(u))du. The linear rescaling u=Ls identifies this with the unit interval velocity integral already used in IntegralCycle; if L=0 the path is constant, all sums and both integrals are zero. This proves classical RS/velocity agreement and orientation-preserving monotone reparameterization invariance without requiring strict monotonicity of a.

For length, differentiability of both real coordinates a.e. reconstructs the real-variable complex derivative. Since G is L-Lipschitz, ‖v(s)‖≤L a.e., hence ∫_0^1‖v(s)‖ds≤L. In fact the candidate module proves the norm bound at every interior point, even at points where a coordinate derivative is missing, by using the zero value of `deriv` in precisely those cases. Therefore the original geometric length bounds the formal velocity length. Applying the baseline defect estimate and multiplying by nonnegative trace suprema gives exactly the manuscript's geometric-length bound.

An exact equality Var(G)=∫‖v‖ is a standard stronger theorem. It is unnecessary for this manuscript estimate. If pursued, the reverse inequality follows by bounding each polygonal increment by ∫‖v‖ and taking the supremum over ordered partitions; the preceding derivative bound proves the other direction for the arclength G.

## Formal checkpoint reached

The three source modules now compile with strict warnings-as-errors. Every numbered RS task above is proved for the source-native standard tagged-partition predicate, including fine-partition existence, uniqueness, continuous monotone transport and zero length. The finite-cycle wrapper identifies the original classical integral with the actual IntegralCycle integral. Exact hashes and compile receipts appear in ANALYTIC_BRIDGE_CLOSEOUT.json.

No correspondence with Mathlib Archive.RiemannStieltjes is claimed or needed for this native formalization: its complete classical tagged-sum definition is present in the source, and has been independently reviewed for semantic adequacy. Canonical general Banach Cauchy/HFC remains a separate open obligation.
