# Arithmetic prime-sieve packet polynomials

Checkpoint SF-DISCOVERY-001. Candidate family developed from the positive seed in Special Functions III, not a historical priority claim. All proofs below concern the exact infinite measure, not a truncation. Floating point examples and checks are separately labeled.

## Definition and domain

Let p be a prime and λ≥−1. Write

\[
x_n=(1-n^{-2})^2,\qquad
\nu_{p,\lambda}=\sum_{n\ge1}\mu(n)^2n^{-4}
 (1+\lambda\mathbf1_{p\mid n})\delta_{x_n}.
\]

The n=1 atom has mass exactly 1 at x=0. It is retained. At λ=0 this is the principal arithmetic packet measure. At λ=−1 it is the conductor-p deletion of all p-divisible squarefree integers. Positive λ increases an entire infinite arithmetic submeasure, rather than adding a finite number of atoms.

For integer depth k≥0 define dν^(k)_(p,λ)=x^k dν_(p,λ). Define P_m^(k;p,λ)(x) as the unique monic polynomial of degree m orthogonal to all lower degrees for this measure. Every Hankel matrix is strictly positive definite: a nonzero polynomial cannot vanish on the infinitely many positive-weight nodes. Hence these polynomials exist for all m, with positive norms, a three-term recurrence, real simple zeros in (0,1), and interlacing. For k≥1 the zero atom is annihilated by the depth tilt, as part of the definition.

The variable x can be complex. The parameters p and k are discrete, while λ is continuous. An optional finite collection of prime strengths uses the multiplicative weight ∏_(p∈F)(1+λ_p 1_(p|n)); the one-prime family is worked completely here.

## Exact arithmetic coordinates

Put D(s)=ζ(s)/ζ(2s). The squarefree Euler factor gives

\[
\sum_{p\mid n}\mu(n)^2n^{-s}=\frac{D(s)}{p^s+1},\qquad \Re s>1.
\]

Therefore the moments are the finite expressions

\[
M_j^{p,\lambda}=\int x^j\,d\nu_{p,\lambda}
=\sum_{r=0}^{2j}(-1)^r{2j\choose r}
\frac{\zeta(4+2r)}{\zeta(8+4r)}
\left(1+\frac\lambda{p^{4+2r}+1}\right).
\]

The depth-k moments are simply M_(k+j)^(p,λ). No infinite numerical sieve is needed to define a finite-degree polynomial.

**Coefficient field.** With v=π^−2, each D(4+2r) is a rational multiple of v^(r+2), by the exact even-zeta formula. Thus M_j^(p,λ)∈Q[v,λ] and every polynomial coefficient belongs to Q(v,λ). At rational λ it belongs to Q(π^−2). This field statement is exact; it is not a numerical recognition claim. For example D(4)=105π^−4, D(6)=675675/(691π^6), and D(8)=34459425/(3617π^8).

Let Δ=M_0 M_2−M_1². The first monic polynomials are

\[
P_0=1,\qquad P_1=x-\frac{M_1}{M_0},
\]
\[
P_2=x^2-\frac{M_0M_3-M_1M_2}{\Delta}x
+\frac{M_1M_3-M_2^2}{\Delta}.
\]

These are exact closed formulas with each M_j given above. In the recurrence P_(m+1)=(x−a_m)P_m−b_m P_(m−1),

\[
a_0=M_1/M_0,\qquad b_1=\Delta/M_0^2,
\]
\[
a_1=\frac{M_0^2M_3-2M_0M_1M_2+M_1^3}{M_0\Delta}.
\]

For p=2 and k=0, the following displayed values are rounded numerical evaluations, not exact decimal constants. The evidence JSON retains 102 significant digits computed at 160-digit working precision.

| Sieve strength | P_1(x) | P_2(x) |
|---|---|---|
| −1 | x−0.0116166975272538704 | x²−0.818736764881443586x+0.0000439811255921053972 |
| 0 | x−0.0443486061020426801 | x²−0.656259153856215709x+0.00108684024880447770 |
| 1 | x−0.0734436359462993999 | x²−0.625917453041842535x+0.00146315754059612105 |

The main mechanism is not the Gram–Schmidt calculation itself. It is the analytic dependence on arithmetic sieve strength and the exact location and collapse of its finite-degree singularities.

## Sieve-strength singularity theorem

Split ν_(p,λ)=ν_nonp+(1+λ)ν_p according to p∤n and p|n. Both submeasures have infinitely many nodes with positive weights. For Hankel order m≥1 put

\[
A_m=[\int x^{i+j}\,d\nu_{\mathrm{non}p}]_{i,j<m},\quad
B_m=[\int x^{i+j}\,d\nu_p]_{i,j<m}.
\]

Both matrices are positive definite. The arithmetic Hankel determinant is

\[
\tau_m(\lambda)=\det(A_m+(1+\lambda)B_m)
=\det A_m\prod_{i=1}^m(1+(1+\lambda)\eta_i),
\]

where η_i>0 are the eigenvalues of A_m^−1/2 B_m A_m^−1/2. Thus τ_m is a polynomial of exact degree m in λ; all m roots, counted with multiplicity, are real and strictly below −1. Every coefficient of P_m is a rational function of λ, and every possible pole lies at one of these Hankel roots. A numerator can cancel a root, so the theorem does not assert that every determinant root is an actual coefficient pole.

This is an application of a known definite matrix-pencil mechanism to a specific arithmetic family. It gives the exact safe domain λ≥−1, including the deletion endpoint. Positive finite matrices beyond the endpoint do not establish positivity of the full signed measure.

## The finite-degree positivity margin collapses

Let −1−δ_m be the Hankel root closest to −1. Then

\[
\delta_m=\min_{0\ne f,\ \deg f<m}
\frac{\int f(x)^2d\nu_{\mathrm{non}p}(x)}
{\int f(x)^2d\nu_p(x)}>0.
\]

The minimum is nonincreasing with m. It tends to zero: choose a continuous bump which equals 1 at the isolated node x_p and 0 at all other nodes, then approximate it uniformly on [0,1] by polynomials. The numerator tends to zero and the denominator remains at least p^−4 asymptotically. Consequently every λ<−1 eventually produces a negative quadratic form at some finite degree. Low-degree positivity can conceal the negative arithmetic submeasure.

For p=2 there is an explicit exponential estimate. The first p-divisible node is x_2=9/16, while every nonzero odd node is at least x_3=64/81. For m≥2 test the Rayleigh quotient with f(x)=x(1−x)^(m−2). It vanishes at the odd zero atom, its denominator includes the n=2 contribution, and its numerator obeys

\[
\int f^2d\nu_{\mathrm{non}2}
\le\left(\frac{16M_0}{17}-1\right)
\left(\frac{17}{81}\right)^{2(m-2)},
\]
\[
\int f^2d\nu_2\ge
\frac1{16}\left(\frac9{16}\right)^2
\left(\frac7{16}\right)^{2(m-2)},
\]

where M_0 denotes the undeformed principal mass 105π^−4. Thus

\[
\boxed{\delta_m\le\frac{4096}{81}
\left(\frac{16M_0}{17}-1\right)
\left(\frac{272}{567}\right)^{2(m-2)}}.
\]

This estimate is a proof, not a fit to the examples. Approximate nearest singularities from the reproducible symmetric pencil calculation are λ_2≈−1.46510834637297762, λ_3≈−1.02378423022945193, and λ_4≈−1.00017511031711379. These numerical roots are not interval-certified roots. The exact proof already locates all the roots.

## Exact depth transport and arithmetic response

The depth change dν^(k+1)=x dν^(k) is the known Christoffel transformation, specialized here to exact arithmetic moments:

\[
P_m^{(k+1)}(x)=\frac{P_{m+1}^{(k)}(x)
-\frac{P_{m+1}^{(k)}(0)}{P_m^{(k)}(0)}P_m^{(k)}(x)}x.
\]

The quotient is a polynomial because its numerator vanishes at zero. Orthogonality follows by canceling x against the new weight. Its denominator P_m^(k)(0) is nonzero, since all zeros of P_m^(k) are strictly positive. This gives exact transport at finite k, rather than only a Laguerre limiting comparison.

For τ_m^(k)=det[M_(k+i+j)]_(i,j<m), with τ_0^(k)=1, the known Desnanot–Jacobi identity gives the discrete tau relation

\[
\tau_m^{(k)}\tau_m^{(k+2)}-(\tau_m^{(k+1)})^2
=\tau_{m+1}^{(k)}\tau_{m-1}^{(k+2)}>0\quad(m\ge1).
\]

In particular every fixed-order shifted Hankel determinant is strictly log-convex in depth. The mechanism is classical; the tau values are explicit arithmetic determinants.

Sieve differentiation is also exact. With h_j(λ)=∫P_j²dν_(p,λ), differentiating the orthogonality relations gives

\[
\partial_\lambda P_m(x;\lambda)
=-\sum_{j<m}\frac{\int P_mP_j\,d\nu_p}{h_j(\lambda)}P_j(x;\lambda),
\qquad
\partial_\lambda h_m=\int P_m^2\,d\nu_p.
\]

This provides a response calculus to prime inclusion, using the same three-term packet basis. It is a general measure-deformation identity, with a specific infinite prime submeasure here.

## Endpoint-mass deformation and recovery

For the undeformed depth-zero measure, let ν_θ=ν+θδ_0 with θ≥−1. Thus θ=−1 removes, rather than ignores, the existing mass 1 at zero. Let K_m(x,y)=Σ_(j=0)^m P_j(x)P_j(y)/h_j. The known Uvarov formula is

\[
P_m^{[\theta]}(x)=P_m(x)
-\frac{\theta P_m(0)}{1+\theta K_{m-1}(0,0)}K_{m-1}(x,0).
\]

Reproduction of lower-degree polynomials by K supplies a direct proof of the orthogonality. It also yields

\[
h_m^{[\theta]}=h_m
\frac{1+\theta K_m(0,0)}{1+\theta K_{m-1}(0,0)}.
\]

For every finite degree, K_m(0,0)<1. The endpoint mass itself is recoverable with a concrete arithmetic gap bound:

\[
\boxed{1\le\frac1{K_m(0,0)}
\le1+(M_0-1)\left(\frac7{16}\right)^{2m}}.
\]

Proof: 1/K_m(0,0) is the least squared norm among polynomials of degree at most m taking the value 1 at zero. The mass-1 zero atom gives the lower bound. The test polynomial (1−x)^m gives the upper bound, because every other node satisfies x≥9/16. Equality with the lower bound at finite degree would require a nonzero polynomial to vanish on infinitely many other nodes, which is impossible. Thus θ=−1 is valid in every finite Uvarov formula, while 1−K_m(0,0) becomes exponentially small. At degree 6, the computed reciprocal kernel is about 1+1.2807666365×10^−18. Omitting the zero atom can produce a large structural change even when normalized bulk plots appear close.

## A precise nonreduction statement

The associated Stieltjes function

\[
S_{p,\lambda}(z)=\int\frac{d\nu_{p,\lambda}(x)}{z-x}
\]

is analytic off the closed arithmetic support and has a genuine isolated simple pole at each positive-weight node x_n. The positive residues cannot cancel. There are infinitely many such nodes tending to 1, including when λ=−1.

Therefore its germ at z=2 is not D-finite in z: no nonzero finite-order linear differential equation with rational coefficients can annihilate it. Such an equation has only finitely many finite singular points, and every solution is analytic at an ordinary point. Infinitely many isolated poles contradict that requirement. This excludes identification of this kernel with a fixed-parameter finite-order rational-ODE special function. It does not exclude every known special function class, nor establish historical novelty. Infinite discrete resolvents commonly have this property.

The generalized hypergeometric and Meijer G classes provide concrete comparisons: their fixed-parameter rational differential equations are documented in DLMF §§16.8 and 16.21, respectively, at https://dlmf.nist.gov/16.8 and https://dlmf.nist.gov/16.21 . Finite sums, products, and rational changes of variable preserve D-finiteness. An expression involving an infinite superposition or a non-D-finite prefactor is outside this specific exclusion.

At the polynomial-sequence level, the entire family cannot be an affine copy of a Jacobi polynomial sequence with a positive continuous weight. Compact moment determinacy would force the corresponding normalized measures to coincide, while ours is purely atomic. It also cannot be an affine copy of the full Laguerre sequence, whose zeros are unbounded as degree grows, while ours remain in a fixed bounded interval. These are limited exact separators. A Laguerre endpoint scaling limit, already present in Special Functions III, remains compatible with both facts.

## Literature classification and search scope

The existence theory, Hankel construction, Christoffel–Darboux kernel, and zero/interlacing facts are classical general orthogonal-polynomial theory. DLMF §18.2 is a verified authoritative reference: https://dlmf.nist.gov/18.2 .

The finite mass modification is classical Uvarov theory. The original article metadata was verified at MathNet: V. B. Uvarov, *The connection between systems of polynomials that are orthogonal with respect to different distribution functions*, 1969, DOI https://doi.org/10.1016/0041-5553(69)90124-4 . The Uvarov identity above is supplied with its local proof; source metadata alone is not used as proof.

Exponential deformation and Toda equations were checked against the primary paper *The kissing polynomials and their Hankel determinants*, which explicitly derives the familiar Toda recurrence flow for an exponential weight: https://academic.oup.com/imatrm/article/6/1/tnab005/6492355 . That is an adjacent known mechanism, not a claim that our arithmetic sieve flow is the same exponential Toda flow.

Bounded web search on 2026-10-08 used the exact queries “orthogonal polynomials squarefree measure”, “orthogonal polynomials zeta Möbius squarefree”, and “orthogonal polynomials prime sieve deformation Hankel”. These searches did not identify this exact node, weight, and prime-strength family. Several “Möbius” hits concerned fractional linear variable changes, which is unrelated to the arithmetic Möbius weight here. Search absence is not evidence of global priority. The present status is **specific candidate family with exact structural results and known construction mechanisms**, with historical novelty unresolved.

The principal squarefree seed and its Gamma–Laguerre limit are inherited from Special Functions III. The continuous prime-strength extension, explicit finite-degree positivity-margin collapse bound, and quantitative zeroatom conditioning analysis are developments of that seed in this checkpoint. They are not asserted to be globally new theorems.

## Computation record and failed first criterion

The reproducible script checks 60 parameter cases: p∈{2,3,5}, λ∈{−1,−1/2,0,1,10}, and k∈{0,1,3,10}, through polynomial degree 6. It tests 1,260 lower-monomial orthogonality conditions, positive norms and recurrence quantities, 24 Uvarov formula cases including full mass removal, 12 definite-pencil calculations through Hankel order 4, three sieve positivity-margin bounds, seven endpoint kernel bounds, 60 exact depth-transport identities, 48 shifted tau identities, and the prime-strength derivative identity. The last identity uses a centered finite difference and is a numerical consistency check. The exact derivative proof above is independent of that check.

**First run failed at the absolute determinant residual criterion** `abs(det(A+(1+λ)B)) < 1e-120`, after the orthogonality/positivity grid had passed. Negative exceptional strengths can have enormous magnitude, so the determinant scale grows as the matrix-entry scale to the Hankel order. The absolute criterion was unsuitable. It was replaced by the dimensionless residual `abs(det(matrix))/max(1,max(abs(matrix entries)))**order < 1e-120`; the run then passed. This numerical correction does not change a mathematical formula or count as an interval root certificate. The first failed criterion is preserved here and in the evidence JSON run history.

Maximum absolute orthogonality residual in the passing run was approximately 1.33365525×10^−161 at 160-digit working precision. These finite floating point checks do not certify all parameter values or historical novelty. The displayed exact theorems are supported by the proofs above.

## Concrete next question

For a single prime, characterize the asymptotic positions and multiplicities of all sieve-strength Hankel roots, not just the nearest root's upper bound. For multiple primes, study the real singular hypersurfaces of the arithmetic Gram determinant and how overlap of prime shelves changes the finite resolution required to expose a signed defect. This is a defined structural research problem with exact input data, rather than an unrestricted invitation to rename a Gram–Schmidt sequence.
