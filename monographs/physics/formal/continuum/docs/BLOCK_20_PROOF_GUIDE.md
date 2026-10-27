# Block 20 — Exact three-dimensional Clifford walk and doubled spectrum

Komorebi Physics Lean v0.20.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF page 41 of 550, printed page 28. The literal targets are equations (8.18)–(8.30). The authoritative cumulative result is `verification/final/report.json`.

## 1. Scope and declaration counts

| Module | Theorems | Other declarations | Role |
|---|---:|---:|---|
| `RelativisticClifford3D` | 26 | 8 | Explicit `4×4` generators, Clifford relations, Hermiticity and traces |
| `InvolutionExponential4` | 27 | 2 | Closed forms, unitarity and determinant-one exponential factors |
| `DiracWalk3D` | 22 | 13 | Literal palindromic walk, exact Clifford reduction, unitarity and determinant |
| `Dispersion3D` | 10 | 2 | Coefficient norm, quadratic shell and principal phase |
| `Spectrum3D` | 14 | 3 | Exact characteristic determinant and doubled phase roots |
| `Relativistic3DExamples` | 17 | 1 | Exact axis, zero-spacing and order-sensitivity witnesses |
| **Block 20** | **116** | **29** | **145 new inventoried declarations** |

The cumulative inventory contains **1,817 theorem declarations, 2,149 inventoried declarations, and 109 mathematical modules**. The 103 Block 19 mathematical modules are protected by `reference/block19_preservation.json`. These are declaration counts, not independent physical discoveries or a completion fraction.

## 2. Explicit Clifford representation: equations (8.18)–(8.20)

The release constructs concrete complex `4×4` matrices

\[
\beta=\sigma_z\otimes I_2,
\quad
\alpha_x=\sigma_x\otimes\sigma_x,
\quad
\alpha_y=\sigma_x\otimes\sigma_y,
\quad
\alpha_z=\sigma_x\otimes\sigma_z.
\]

No Clifford law is a structure field. Entrywise matrix multiplication proves

\[
\boxed{\alpha_i\alpha_j+\alpha_j\alpha_i=2\delta_{ij}I_4,}
\]

\[
\boxed{\alpha_i\beta+\beta\alpha_i=0,\qquad \beta^2=I_4.}
\]

Every generator is also proved Hermitian and traceless. The indexed theorems are `alpha_clifford`, `alpha_beta_anticommute`, `alpha_sq`, `alpha_hermitian`, and `trace_alpha`.

## 3. Literal exponential factors and the palindromic walk

The actual matrix exponential is retained in the definitions

\[
M_{1/2}=e^{-im\Delta\beta/2},\quad
X_{1/2}=e^{-ik_x\Delta\alpha_x/2},\quad
Y_{1/2}=e^{-ik_y\Delta\alpha_y/2},\quad
Z=e^{-ik_z\Delta\alpha_z}.
\]

The literal update is

\[
U_\Delta=M_{1/2}X_{1/2}Y_{1/2}ZY_{1/2}X_{1/2}M_{1/2}.
\]

`InvolutionExponential4` first proves the needed exponential identities from the diagonal `β` factor and an explicit invertible Clifford bridge. It then proves each factor unitary and determinant one. `DiracWalk3D.walk_unitary`, `walk_unitary_left`, `walk_unitary_right`, and `det_walk` prove the corresponding exact statements for the seven-factor product.

The order is significant. A checked quarter-turn witness proves that the `x` and `y` Clifford factors do not commute.

## 4. Exact closed form and shell

Successive use of the palindromic sandwich identity gives

\[
\boxed{U_\Delta=C_\Delta I_4-iV_\Delta,}
\]

where

\[
C_\Delta=
\cos(m\Delta)\cos(k_x\Delta)\cos(k_y\Delta)\cos(k_z\Delta)
\]

and

\[
\begin{aligned}
V_\Delta={}&
\sin(m\Delta)\cos(k_x\Delta)\cos(k_y\Delta)\cos(k_z\Delta)\,\beta\\
&+\sin(k_x\Delta)\cos(k_y\Delta)\cos(k_z\Delta)\,\alpha_x\\
&+\sin(k_y\Delta)\cos(k_z\Delta)\,\alpha_y
+\sin(k_z\Delta)\,\alpha_z.
\end{aligned}
\]

The theorem `walk_eq_closedWalk` proves this for the literal exponential product. It is not used as the definition of the walk.

The scalar coefficient is proved to lie in `[-1,1]`, and

\[
\operatorname{Tr}U_\Delta=4C_\Delta.
\]

The microcell identity `2 * (Δ/2) = Δ` checks the source convention in (8.26), but it does not by itself formalize a position-space locality theorem.

## 5. Quadratic shell relation

The four Clifford coefficients telescope exactly:

\[
\|V_\Delta\|_{\mathrm{Cliff}}^2=1-C_\Delta^2.
\]

More precisely, `vectorPart_sq` proves

\[
V_\Delta^2=(1-C_\Delta^2)I_4.
\]

Consequently the literal walk satisfies

\[
\boxed{U_\Delta^2-2C_\Delta U_\Delta+I_4=0.}
\]

The principal phase is defined by

\[
\phi_\Delta=\arccos C_\Delta,
\quad 0\le\phi_\Delta\le\pi,
\]

and Lean proves

\[
\cos\phi_\Delta=C_\Delta.
\]

For `Δ ≠ 0`, the frequency `ω_Δ=φ_Δ/Δ` obeys the exact shell (8.30). No small-spacing expansion is claimed here.

## 6. Characteristic polynomial and doubled roots

For a generic Clifford pencil, the release proves the exact determinant identity

\[
\det(xI+a\beta+b\alpha_x+c\alpha_y+d\alpha_z)
=(x^2+a^2+b^2+c^2+d^2)^2.
\]

Substitution of the exact walk coefficients gives

\[
\boxed{
\det(zI_4-U_\Delta)
=(z^2-2C_\Delta z+1)^2.
}
\]

This is equation (8.28). Define

\[
r_-=e^{-i\phi_\Delta},\qquad r_+=e^{i\phi_\Delta}.
\]

Lean proves

\[
r_-r_+=1,
\qquad r_-+r_+=2C_\Delta,
\]

and therefore

\[
\boxed{
\det(zI_4-U_\Delta)
=(z-r_-)^2(z-r_+)^2.
}
\]

Each root has unit modulus and zeros the characteristic determinant. This realizes the doubled spectral branches in (8.29). It does not assert that the two roots are distinct at every parameter: at phases `0` or `π` they coincide and the characteristic root is quadruple.

## 7. Exact witnesses and rejection tests

At `m=kx=ky=0`, `kz=1`, and `Δ=π/2`, Lean proves

\[
C_\Delta=0,
\quad
U_\Delta=-i\alpha_z,
\quad
\det U_\Delta=1,
\]

\[
\det(zI-U_\Delta)=(z^2+1)^2,
\quad
r_-=-i,
\quad r_+=i.
\]

The walk is nonidentity and the roots are distinct. At all zero parameters the walk is exactly `I_4` and the characteristic polynomial is `(z-1)^4`, checking the coincident-branch boundary. Opposite `z` momenta give distinct updates.

Seven new deliberately false controls reject commuting Clifford generators, an identity axis walk, determinant `-1`, an unsquared characteristic polynomial, order independence, coincident axis roots, and the wrong phase sign.

## 8. Boundaries and next target

This block checks equations (8.18)–(8.30) in the explicit complex `4×4` realization. It does not prove the small-spacing expansion (8.31)–(8.36), the axis–diagonal anisotropy (8.37)–(8.41), or the observer-shell defect (8.42)–(8.48). It also does not claim empirical validity or a position-space implementation of locality.

The next block should prove the genuine sixth-order Taylor expansion of the four-cosine shell and then invert it on the positive-spacing branch to obtain the `Q(k)/(6E)` correction and continuum velocity.
