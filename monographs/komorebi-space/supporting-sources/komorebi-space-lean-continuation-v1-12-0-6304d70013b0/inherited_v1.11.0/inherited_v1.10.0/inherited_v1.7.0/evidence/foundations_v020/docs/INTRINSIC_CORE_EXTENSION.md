# Komorebi Space Theory: intrinsic core and splitting changes
## v0.4.0 · Komorebi P.

This extension distinguishes the invariant spaces attached to a fixed differential from the nonunique choices of correction and protected coordinates. It constructs and compares the coordinate maps, proves their cocycle and norm bounds, and exhibits two distinct repairs on the same dimension-growing towers. It does not select an intrinsic resolution doctrine.

## 1. Fixed differential, variable section

Let \(\mathbb K\) be a nontrivially normed field. Let \(E,R\) be normed \(\mathbb K\)-spaces and let
\[
 d:E\longrightarrow R
\]
be continuous linear. Define
\[
 \boxed{E^0=\ker d.}
\]
A section is a continuous linear map
\[
 A:R\longrightarrow E,\qquad dA=I_R.
\]
Neither \(E^0\) nor \(R\) depends on \(A\). A section is additional data. Existence of a section is not inferred from the notation.

Define
\[
 \boxed{P_A=I_E-Ad.}
\]
Then
\[
 dP_A=0,\qquad P_A^2=P_A,\qquad P_A|_{E^0}=I_{E^0},\qquad P_AA=0.
\]
Completeness is not required for these statements or for the coordinate equivalence below.

**Lean:** `SplitDefect.Section`, `Core`, `Section.project`, `project_exact`, `project_idempotent`, `project_fixes`, `project_lift`.

## 2. Coordinates on a fixed product

For each section define
\[
 \boxed{
 \begin{aligned}
 \Psi_A:E&\longrightarrow E^0\times R,&
 \Psi_A(f)&=(P_Af,df),\\
 \Psi_A^{-1}(e,r)&=e+Ar.
 \end{aligned}}
\]
The identities
\[
 (f-Adf)+Adf=f,\quad d(e+Ar)=r,\quad P_A(e+Ar)=e
\]
prove that these maps are inverse. They are linear and satisfy
\[
 \|\Psi_Af\|\le\max(\|P_A\|,\|d\|)\|f\|,
\]
\[
 \|\Psi_A^{-1}(e,r)\|\le(1+\|A\|)\|(e,r)\|.
\]
Thus
\[
 \boxed{E\simeq_L E^0\times R.}
\]
The product uses the maximum norm. This is a continuous linear equivalence, not an isometry. The factors are fixed, but the coordinate map depends on the section.

**Lean:** `Section.chartLinear`, `chart_bound`, `chart_inverse_bound`, `chart`, `chart_exact_component`, `chart_residual`, `chart_inverse`.

## 3. Exact change-of-chart law

Let \(A,B\) be two sections. Since
\[
 d(A-B)=0,
\]
the map \(A-B\) takes values in \(E^0\). Define
\[
 T_{A\to B}=\Psi_B\Psi_A^{-1}.
\]
Direct substitution yields
\[
 \boxed{T_{A\to B}(e,r)=(e+(A-B)r,r).}
\]
In particular,
\[
 T_{A\to B}(e,0)=(e,0).
\]
The exact slice is fixed pointwise, and every residual coordinate is unchanged. For three sections,
\[
 \boxed{T_{B\to C}T_{A\to B}=T_{A\to C},\qquad T_{A\to A}=I.}
\]
This follows from \((A-B)+(B-C)=A-C\). The transition maps are actual continuous linear equivalences and obey
\[
 \boxed{\|T_{A\to B}(e,r)\|\le(1+\|A-B\|)\|(e,r)\|.}
\]
These are triangular shear maps. Calling them coordinate changes does not assert manifold charts, a stack, or curvature classes beyond this defined linear system.

**Lean:** `Section.difference`, `difference_exact`, `difference_add`, `transition`, `transition_formula`, `transition_residual`, `transition_exact_slice`, `transition_cocycle`, `transition_norm`.

## 4. All sections and all retractions

Fix one section \(A\). For each bounded linear map \(T:R\to E^0\), let \(\iota:E^0\hookrightarrow E\) be inclusion and define
\[
 A_T=A+\iota T.
\]
Then \(dA_T=I\). Conversely, every section \(B\) has the unique form
\[
 B=A+\iota T,\qquad T=B-A\in\mathcal L(R,E^0).
\]
The package constructs the bijection
\[
 \boxed{\mathcal L(R,E^0)\simeq\{B\in\mathcal L(R,E):dB=I\}.}
\]
This parametrizes sections relative to a chosen base section. It does not designate a preferred one.

For the corresponding retractions,
\[
 \boxed{P_Bf-P_Af=(A-B)df.}
\]
Therefore
\[
 \|P_Bf-P_Af\|\le\|A-B\|\|df\|.
\]
Also
\[
 P_AP_B=P_B,\qquad P_BP_A=P_A,
\]
so
\[
 \boxed{P_AP_B=P_BP_A\iff P_A=P_B\iff A=B.}
\]
All sections give identical repair on exact inputs. On nonexact inputs, the repairs can differ by a nonzero exact element.

**Lean:** `Section.translate`, `sectionParameters`, `project_change`, `project_change_norm`, `project_other`, `projects_commute_iff`, `projects_equal_iff_lifts_equal`.

## 5. Application to the actual resolution towers

Retain the v0.3.0 towers and differential
\[
 E=\ell^\infty_n\mathcal L(X_n,Y_n),\quad
 R=\ell^\infty_n\mathcal L(X_{n+1},Y_n),
\]
\[
 (df)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.
\]
Let \(L=(s_n^L)\), \(M=(s_n^M)\) be two uniformly bounded target splittings, with
\[
 \rho^Y_ns_n^L=I=\rho^Y_ns_n^M,
\]
\[
 \|s_n^L\|\le S_L,\quad\|s_n^M\|\le S_M,\quad
 \|\rho^X_n\|\le B,
\]
and
\[
 S_LB<1,\qquad S_MB<1.
\]
The already constructed causal corrections \(A_L,A_M\) are sections of this actual differential. All results in Sections 1–4 apply to them. In particular,
\[
 \boxed{P_Mf-P_Lf=(A_L-A_M)df.}
\]
The generic exact core is proved to be the existing tower-compatibility kernel, rather than an unrelated abstract space.

**Lean:** `Splitting.defectSection`, `coreCoordinates`, `coreTransition`, `coreTransition_formula`, `coreTransition_cocycle`, `correction_difference_exact`, `repair_change`, `repair_change_norm`, `repair_change_gain_bound`, `repair_cross`, `repairs_commute_iff`, `repairs_agree_on_exact`.

## 6. The protected-profile space is also splitting-independent

The v0.3.0 protected observable is
\[
 (p_Lf)_0=f_0,\qquad
 (p_Lf)_{n+1}=(I-s_n^L\rho^Y_n)f_{n+1}.
\]
Define its fixed-point subspace \(\mathcal S_L=\{f:p_Lf=f\}\). Then
\[
 \boxed{f\in\mathcal S_L\iff
   \forall n,\ \rho^Y_nf_{n+1}=0.}
\]
Indeed, the forward direction follows by applying \(\rho^Y_n\) to the innovation expression. Conversely, each profile with values in the indicated kernels is fixed by every \(p_L\). The initial coordinate is unrestricted.

Consequently,
\[
 \boxed{\mathcal S_L=\mathcal S_M,\qquad p_Lp_M=p_M.}
\]
This is literal equality of submodules inside the same bounded candidate space. It does not imply \(p_Lf=p_Mf\) for arbitrary \(f\). The possible profile values are invariant, while the profile assigned to a candidate can change.

**Lean:** `Splitting.semanticSpace_characterization`, `semanticSpace_eq`, `observable_cross`.

## 7. Quantitative splitting stability

Assume also
\[
 \|s_n^L-s_n^M\|\le\varepsilon\quad(\forall n),\qquad\varepsilon\ge0.
\]
Define
\[
 \boxed{C_{L,M}(\varepsilon)=
 \frac{\varepsilon}{(1-S_LB)(1-S_MB)}.}
\]
Then
\[
 \boxed{\|A_L-A_M\|\le C_{L,M}(\varepsilon).}
\]
In consequence,
\[
 \boxed{\|P_Mf-P_Lf\|\le C_{L,M}(\varepsilon)\|df\|,}
\]
\[
 \|P_M-P_L\|\le C_{L,M}(\varepsilon)(B+B_Y).
\]
The gap factors are positive by hypothesis. The bound can deteriorate near a propagation threshold. No sharpness claim is made.

### Proof

Write \(a_n=(A_Lr)_n\), \(b_n=(A_Mr)_n\). The exact recurrence is
\[
 a_{n+1}-b_{n+1}
 =s_n^L(a_n-b_n)\rho^X_n
 +(s_n^L-s_n^M)(r_n+b_n\rho^X_n).
\]
Using \(\|b_n\|\le K_M\|r\|\), with \(K_M=S_M/(1-S_MB)\), induction gives
\[
 \|a_{n+1}-b_{n+1}\|
 \le S_LB C_{L,M}\|r\|
   +\varepsilon(1+BK_M)\|r\|
 =C_{L,M}\|r\|.
\]
The initial difference is zero. Taking the supremum and then the operator norm proves the result. The repair bound follows from Section 5.

**Lean:** `Splitting.perturbationGain`, `perturbationGain_balance`, `rawCorrection_difference_succ`, `rawCorrection_perturbation`, `correction_perturbation`, `correction_perturbation_opNorm`, `repair_perturbation`, `repair_perturbation_opNorm`.

## 8. Two splittings, one tower, different exact repairs

Use the same checked dimension-growing towers
\[
 X_n=Y_n=\mathbb R^{n+1},\quad
 \rho^X_n=\tfrac12\pi_n,\quad \rho^Y_n=\pi_n.
\]
Here \(\pi_n\) deletes the last coordinate. Compare
\[
 s_n^0(y)=(y,0),\qquad s_n^1(y)=(y,y_0).
\]
Both have norm at most one under the sup norms, both are right inverses, and both satisfy the propagation gap \(1\cdot\tfrac12<1\).

For the candidate \(f_n=I\), the repaired stage-one operators are
\[
 \boxed{
 (P_0f)_1=\begin{pmatrix}1/2&0\\0&1\end{pmatrix},\qquad
 (P_1f)_1=\begin{pmatrix}1/2&0\\-1/2&1\end{pmatrix}.}
\]
The proof checks both coordinate formulas for arbitrary inputs, not only sampled vectors. The full infinite families are exact and have the same initial operator, but they are unequal. The corresponding retraction operators do not commute. The protected profile subspaces are equal, but the protected values of the original candidate differ.

**Lean:** `SplittingDependence.skewSplitting`, `skew_gap`, `skewRepair_exact`, `skew_identity_first_new`, `skew_identity_first_old`, `exact_repairs_differ`, `profile_spaces_equal`, `protected_profiles_differ`, `repair_operators_do_not_commute`, `same_seed_distinct_exact_repairs`.

## 9. What is canonical here?

For fixed towers, bonding maps and norms:
\[
 \boxed{E,\ R,\ d,\ \ker d,\ \mathcal S}
\]
are independent of the chosen target splitting. In contrast,
\[
 \boxed{A_L,\ P_L,\ p_L,\ \Psi_L}
\]
can depend on that choice. The dependency is described by proved continuous linear changes of coordinates and quantitative estimates.

This is not canonicity under arbitrary replacement of the towers, reindexing, changes of norm, semantic doctrine, or ambient category. It is not a construction of the earlier proposed stack or unrestricted pro-category theory.

## 10. Verification boundary and established mathematics

The abstract decomposition is a bounded splitting of the exact sequence
\[
 0\longrightarrow\ker d\longrightarrow E\xrightarrow{d}R\longrightarrow0.
\]
Such splitting constructions are established mathematics. The pinned mathlib contains `ContinuousLinearEquiv.equivOfRightInverse` in `Mathlib/Topology/Algebra/Module/Equiv.lean`; the current module constructs the kernel-first chart explicitly to expose its bounds and change-of-chart laws. No novelty claim is made for the abstract splitting argument.

The extension's role is to connect these facts to the actual tower correction, distinguish the invariant and choice-dependent pieces, derive the two-gap stability estimate, and verify the same-tower counterexample.

The supplementary rational script checks 144 deterministic finite cases, 1,876 positive assertions, and two rejected mutations. It is an independent implementation audit, not a substitute for the universally quantified Lean proofs.
