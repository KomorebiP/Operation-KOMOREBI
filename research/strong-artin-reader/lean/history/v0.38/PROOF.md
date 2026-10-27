# Mathematical proof and formal correspondence

All p-adic norms below have |p|=p^(-1). Matrix norms are entrywise suprema. The finite index type is nonempty. No diagonalization or commutativity of the matrices is assumed.

## 1. Ordered expansion

For a norm-one, complete ultrametric normed ring E and ||A||<=1, set

\[
D_d(h)=\sum_{i=0}^{d-1} A^i h A^{d-1-i},\qquad
R_d(h)=(A+h)^d-A^d-D_d(h).
\]

The formal recursive definition satisfies D_(d+1)(h)=D_d(h)A+A^d h. `tangent_eq_sum` identifies it with the full ordered sum. Linearity/additivity are proved, not substituted for the power map.

The identity

\[
R_{d+1}(h)=R_d(h)(A+h)+D_d(h)h
\]

preserves the order of every factor. Subtracting the identities at h and k gives

\[
\begin{aligned}
R_{d+1}(h)-R_{d+1}(k)
={}&(R_d(h)-R_d(k))(A+h)+R_d(k)(h-k)\\
&+(D_d(h)-D_d(k))h+D_d(k)(h-k).
\end{aligned}
\]

Ultrametricity, submultiplicativity, and induction yield, for 0<=rho<=1 and ||h||,||k||<=rho,

\[
\|D_d(h)\|\le\|h\|,\qquad
\|R_d(h)-R_d(k)\|\le\rho\|h-k\|.
\]

There is no factor depending on the degree or matrix dimension in these estimates. The ultrametric triangle inequality is essential. Declarations: `norm_tangent_le`, `remainder_lipschitz`, `remainder_bound`.

## 2. Exact local image by contraction

Let Q be an additive two-sided inverse of D_d, with ||Qz||<=K||z||, K>=0 and K rho<1. Put delta=U-A^d. On the closed rho-ball consider

\[
f(h)=Q(\delta-R_d(h)).
\]

If ||Q delta||<=rho, this map preserves the ball and has Lipschitz constant K rho<1. The closed ball is complete. Mathlib's Banach fixed-point theorem supplies a fixed point h. Applying D_d to the fixed-point equation proves (A+h)^d=U. The strict contraction proves uniqueness in that ball.

Conversely, any root A+h in the ball satisfies Q delta=h+Q R_d(h), so ||Q delta||<=rho. Thus both existence alone and unique existence are equivalent to the inverse-image norm condition. These are `power_ball_exists_iff` and `power_ball_image`.

The Banach theorem used is `ContractingWith.exists_fixedPoint'` from the pinned `Mathlib/Topology/MetricSpace/Contracting.lean`. The current public [API documentation](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/MetricSpace/Contracting.html) is a reading aid; the compiler uses the recorded pinned source. This is a standard contraction argument, with no historical novelty claim.

## 3. Actual p-adic matrices

`padic_matrix_mul_bound` proves submultiplicativity of the entrywise supremum norm over Q_p. `padicMatrixUltra` and `padicMatrixComplete` establish the other hypotheses of the abstract theorem for Mat_n(Q_p). The norm is the ordinary finite-product norm, so completeness is inherited from Q_p.

`integralMatrix` embeds Mat_n(Z_p) entry by entry and is injective. `matrix_reduction_iff_norm` identifies congruence modulo p^m with distance <=p^(-m). A root in a radius <=1 ball about an integral center has integral entries, and the formal proof constructs those entries as actual elements of Mathlib's `PadicInt`.

## 4. Finite inverse certificate and precision

B is an integral coefficient matrix with pair-indexed rows and columns. `coefficientAction` is its action over Q_p; `integralAction` is its action over Z_p. Their compatibility is proved. Integral coefficients give ||Bx||<=||x||.

Define Q=p^(-s)B. `InverseCertificate` checks QD_A(E_ij)=E_ij and D_AQ(E_ij)=E_ij for every matrix unit. `linear_identity_of_matrix_basis` and the left/right certificate theorems extend these equalities to every matrix. The hypotheses really assert a two-sided inverse over Q_p; a singular operator cannot pass them.

`inverseLinear_norm` gives K=p^s. Taking rho=p^(-m), the inequality m>s gives K rho=p^(s-m)<1. The exact norm criterion becomes

\[
\|Q(U-A^d)\|\le p^{-m}
\iff \|B(U-A^d)\|\le p^{-(m+s)}
\iff B\operatorname{vec}(U-A^d)=0\pmod{p^{m+s}}.
\]

This is `inverse_norm_iff_congruence`. `integral_test_iff_finite` pushes all coefficients and operations into the finite residue ring. Consequently, once the exact inverse certificate is supplied, **one finite target test** decides the local root problem.

## 5. Units and scope

`matrix_power_unique_iff` gives unique integral matrices. For d>0 and U a unit, F^d=U implies F is a unit in any monoid. `matrix_unit_root_iff` constructs the corresponding matrix-ring unit and transfers uniqueness by injectivity of its value map. `matrix_unit_root_finite_iff` is the final finite-ring statement.

No further compactness or all-depth solvability hypothesis enters this argument. The output's reductions automatically form a compatible root tower. This release does not formalize an identification with a local Galois representation, prove simultaneous conjugacy prescriptions in this new sector, or deduce global automorphy.

The parameter s measures inverse-derivative denominators and can exceed v_p(d); in the square-map unipotent example s=2 while v_2(2)=1. Substituting the scalar valuation for s would be unjustified.
