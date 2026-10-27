# Paper IX: perturbation theory, nearby roots, and deformation

Komorebi P. — 8 September 2026

This note connects the earlier seed-lifting manuscripts to the current Paper IX polynomial lifting formalization. The new statements below have written proofs; they are **not new Lean-checked declarations**. The existing tower release and its verification report remain unchanged.

## Recovered results and corrected status

The earlier theory is directly relevant:

- **Universal_Seed_Lifting.tex, §5, “Multivariable Hensel uniqueness.”** A polynomial system with an invertible residual square Jacobian has exactly one root in its residual ball. The manuscript gives the digit-by-digit proof. Consequently, the previous checklist's square-uniqueness item is a Lean formalization task, not a missing mathematical route.
- **Seed_Lifting.pdf, Theorem 5.1, pp. 9–10.** The weighted inverse expands a positive-depth perturbation of an invertible operator as a convergent series. For this note only a single finite matrix perturbation is needed.
- **Seed_Lifting.pdf, Theorem 6.1, p. 11.** Scalar dyadic lifting permits a nonunit derivative when the residual valuation is greater than twice the derivative valuation.
- **Seed_Lifting.pdf, Theorem 7.1, pp. 12–13.** Smith weights give the solvability conditions and exact counts for linear corrections. The manuscript explicitly leaves nonlinear remainder control as an additional obligation.
- **Projector_Resolved_Seed_Calculus_X.pdf, Theorem 4.2, pp. 8–9.** Projectors commuting with a differential split its cohomology into packets. Applying this to a new deformation problem requires the actual controlling complex and commuting projectors; a packet label alone does not establish the hypothesis.

The current checked Paper IX machinery supplies actual polynomial Taylor remainders, finite cokernel obstructions, correction torsors, exact residue-lift counts, compatible smooth towers, and exact p-adic root existence. Its lifting interface currently starts with **integer** polynomial coefficients and an **integer** approximate root. The p-adic coefficient statements in this note require a new formal interface.

## 1. Notation and the precision lost by inversion

Fix a prime \(p\), and write \(R=\mathbb Z_p\), \(K=\mathbb Q_p\). All polynomial systems have finitely many variables and equations. For a vector or matrix, divisibility by \(p^n\) means divisibility of every entry. Set

\[
v(z)=\min_i v_p(z_i),\qquad v(0)=+\infty.
\]

Let \(d\ge1\), and let \(J\in M_d(R)\) be invertible over \(K\). Choose an integer \(s\ge0\) such that

\[
p^sJ^{-1}\in M_d(R).
\tag{1}
\]

Thus applying \(J^{-1}\) loses at most \(s\) digits:
\(v(J^{-1}z)\ge v(z)-s\).
The least possible \(s\) is the largest Smith exponent of \(J\), rather than the sum of all Smith exponents. No Smith normal form is needed for the proofs: the explicit condition (1) suffices. For a unit Jacobian, \(s=0\).

## 2. Integral Taylor estimates

For \(F\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), and \(J=DF(a)\), write

\[
F(a+h)=F(a)+Jh+Q(h).
\tag{2}
\]

Translation by the integral vector \(a\) leaves all coefficients integral. After subtracting the constant and linear terms, every monomial of \(Q\) has total degree at least two. Therefore, for \(h,k\in p^tR^d\), \(t\ge0\),

\[
v(Q(h))\ge2v(h),\qquad
v(Q(h)-Q(k))\ge v(h-k)+t.
\tag{3}
\]

For the second inequality, telescope each difference of monomials into terms with one factor \(h_i-k_i\). At least one other factor belongs to \(p^tR\). An arbitrary integral polynomial \(H\) similarly satisfies

\[
v(H(a+h)-H(a+k))\ge v(h-k).
\tag{4}
\]

These elementary estimates are the p-adic coefficient counterparts of the already checked integer Taylor bridge.

## 3. Strong vector lifting with a nonunit Jacobian

**Theorem.** Suppose \(F\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), \(J=DF(a)\) is invertible over \(K\), and (1) holds. If \(r\) is an integer with

\[
F(a)\in p^rR^d,\qquad r>2s,
\tag{5}
\]

then there is exactly one \(b\in a+p^{s+1}R^d\) satisfying \(F(b)=0\). Moreover,

\[
b-a\in p^{r-s}R^d.
\tag{6}
\]

**Proof.** Define

\[
\Phi(h)=-J^{-1}F(a)-J^{-1}Q(h).
\]

On the complete ball \(B=p^{s+1}R^d\), the constant term has valuation at least \(r-s\ge s+1\), while the nonlinear term has valuation at least \(s+2\). Thus \(\Phi(B)\subseteq B\). Equation (3) gives

\[
v(\Phi(h)-\Phi(k))\ge v(h-k)+1.
\tag{7}
\]

Starting at \(h_0=0\) and setting \(h_{n+1}=\Phi(h_n)\), successive differences gain at least one digit at each iteration. The sequence is Cauchy and converges in \(B\); continuity makes its limit a fixed point. Two distinct fixed points would contradict (7), so the fixed point is unique throughout \(B\). Fixed points are precisely roots of \(F(a+h)\).

The smaller ball \(B'=p^{r-s}R^d\) is also preserved: its nonlinear term has valuation at least \(2(r-s)-s\ge r-s\). Since the iteration starts in \(B'\), the limit lies in \(B'\). This proves (6). This argument also covers \(F(a)=0\), without assigning a finite valuation to zero. ∎

This is a sufficient criterion for systems whose Jacobian may be singular modulo \(p\) but is invertible over \(\mathbb Q_p\). It does not cover every singular system.

## 4. Nearby roots under coefficient perturbation

**Theorem.** Suppose \(F(a)=0\) and the same Jacobian hypothesis (1) holds. For an integer \(M\), let

\[
G=F+p^M H,\qquad H\in R[X_1,\ldots,X_d]^d,\qquad M>2s.
\tag{8}
\]

Then \(G\) has exactly one root \(b\) in \(a+p^{s+1}R^d\), and

\[
\boxed{\quad b\equiv a\pmod{p^{M-s}}.\quad}
\tag{9}
\]

**Direct proof.** With \(Q\) as in (2), use the fixed original Jacobian:

\[
\Psi(h)=-J^{-1}\bigl(Q(h)+p^MH(a+h)\bigr).
\tag{10}
\]

On \(p^{s+1}R^d\), the quadratic part gains at least one digit in differences, while the perturbation part gains at least \(M-s\ge1\), by (3)–(4). Both terms map the ball into itself. The iteration argument of §3 proves a unique fixed point there. The smaller ball \(p^{M-s}R^d\) is preserved as well: the two output valuations are at least \(2(M-s)-s\) and \(M-s\). Thus (9) follows. ∎

**Connection to the earlier weighted inverse.** Alternatively,

\[
DG(a)=J(I+E),\qquad E=p^M J^{-1}DH(a)\in p^{M-s}M_d(R).
\]

Since \(M-s\ge1\),

\[
(DG(a))^{-1}=\left(\sum_{n\ge0}(-E)^n\right)J^{-1},
\]

so \(p^s(DG(a))^{-1}\) remains integral. Applying §3 to \(G\) gives the same conclusion. This finite matrix instance makes the weighted inverse's role explicit without any issue of infinite packet indexing.

**First-order displacement with a controlled remainder.** Equation (10) and \(v(b-a)\ge M-s\) give

\[
b-a=-p^MJ^{-1}H(a)+\varepsilon,
\qquad \varepsilon\in p^{2M-3s}R^d.
\tag{10a}
\]

Indeed, the quadratic remainder after applying \(J^{-1}\) has valuation at least \(2(M-s)-s\); the difference \(p^MJ^{-1}(H(b)-H(a))\) has valuation at least \(2M-2s\). Both are divisible by \(p^{2M-3s}\). Since \(M>2s\), this error is deeper than the guaranteed displacement depth \(M-s\).

The displacement bound is attained for \(F(X)=p^sX\), \(a=0\), \(H=1\). The error bound is attained for \(F(X)=p^sX+X^2\), \(a=0\), \(H=1\): the selected root has valuation \(M-s\), and \(b+p^{M-s}=-p^{-s}b^2\) has valuation \(2M-3s\).

**Why strict depth matters.** Take \(p=2\), \(F(X)=X^2-1\), \(a=1\), \(s=1\). At the excluded boundary \(M=2s=2\), the perturbation

\[
G(X)=F(X)+4=X^2+3
\]

has no root in \(\mathbb Z_2\): it would require a square congruent to \(5\pmod8\), whereas squares modulo 8 are \(0,1,4\). Thus \(M\ge2s\) is not a valid uniform replacement for \(M>2s\).

## 5. Parameter deformations and rectangular charts

Let \(F(X,T)\in R[X_1,\ldots,X_d,T_1,\ldots,T_q]^d\), with \(F(a,t_0)=0\). Assume \(J=D_XF(a,t_0)\) satisfies (1). Fix an integer \(M_0>2s\).

For every \(t\in t_0+p^{M_0}R^q\), coefficientwise polynomial congruence gives

\[
F(X,t)-F(X,t_0)\in p^{M_0}R[X]^d.
\]

Section 4 therefore defines a unique solution \(b(t)\in a+p^{s+1}R^d\), with

\[
F(b(t),t)=0,\qquad b(t)-a\in p^{M_0-s}R^d.
\tag{11}
\]

For \(t,t'\) in this parameter ball and an integer \(N\ge M_0\),

\[
t\equiv t'\pmod{p^N}
\quad\Longrightarrow\quad
b(t)\equiv b(t')\pmod{p^{N-s}}.
\tag{12}
\]

To prove (12), use the common fixed Jacobian and write the fixed-point equation (10) for the two parameter values. Changing the parameter at a fixed argument changes its right-hand side by an element of \(p^{N-s}R^d\). Changing the argument gains at least one digit. If the two fixed points differed at a valuation smaller than \(N-s\), these two estimates would force their difference to have strictly larger valuation than itself, a contradiction. Thus the root response is continuous with a quantified loss of at most \(s\) digits.

For a rectangular polynomial system \(F:R^D\to R^e\), \(e\ge1\), with surjective Jacobian modulo \(p\) at an exact root, choose an invertible \(e\times e\) minor and split variables into \(Y\in R^e\) and \(T\in R^{D-e}\). The minor has \(s=0\). Applying (11) with \(M_0=1\) proves that the roots in the chosen residual ball form exactly a graph

\[
\{(\phi(t),t):t\in t_0+pR^{D-e}\}.
\tag{13}
\]

The map \(\phi\) is 1-Lipschitz by (12). This establishes a continuous local parametrization by the free coordinates. Analyticity and the derivative formula require an additional argument and are not claimed here as formalized results.

## 6. The exact first-order obstruction for prescribed parameters

Let \(F\in\mathbb Z[X_1,\ldots,X_d,T_1,\ldots,T_q]^e\). At an integer approximate solution \((x,\lambda)\in\mathbb Z^d\times\mathbb Z^q\) with \(F(x,\lambda)=p^n r\), \(r\in\mathbb Z^e\), and an integer \(n\ge1\), put

\[
J=D_XF(x,\lambda)\bmod p,\qquad
K=D_TF(x,\lambda)\bmod p.
\]

For a prescribed parameter digit \(v\in\mathbb F_p^q\), seek a solution digit \(u\in\mathbb F_p^d\). Choose integer representatives \(\widetilde u,\widetilde v\) and form the next point \((x+p^n\widetilde u,\lambda+p^n\widetilde v)\). Taylor expansion modulo \(p^{n+1}\) gives the correcting equation

\[
Ju=-\bar r-Kv.
\tag{14}
\]

The obstruction is \([\bar r+Kv]\in\operatorname{coker}J\). It vanishes exactly when a correction exists. A nonempty correction set is a torsor for \(\ker J\) and has \(p^{d-\operatorname{rank}J}\) elements. These are direct mathematical specializations of the checked Taylor and finite-fiber APIs; the split-parameter declaration is still to be written.

The relevant derivative is with respect to the variables being solved for. For example, \(F(X,T)=X^2-T\) has surjective total Jacobian at \((0,0)\), yet \(T=p^{2k+1}\) has no root in \(\mathbb Z_p\), for any \(k\ge0\). A square has even valuation. Hence arbitrarily small prescribed parameter changes can be obstructed despite smoothness of the total solution space.

## 7. Revised next-block checklist

| Item | Current evidence | Exact work left |
|---|---|---|
| Square root uniqueness | Written proof recovered from the earlier manuscript | Formalize reduction of arbitrary p-adic roots, then use the checked one-child count and equality at every precision. |
| Integer coefficient perturbation, surjective Jacobian | Immediate corollary of the current checked existence theorem | Add the coefficient/Jacobian congruence interface for \(G=F+p^M H\). |
| Nearby-root stability, unit square Jacobian | Written proof in this note; compatible with the prior uniqueness proof | Connect the unique roots at precision \(M\) and check the resulting theorem in Lean. |
| Rectangular local parametrization | Continuous graph proved in §5 | Formalize variable splitting, parameter specialization, and passage to arbitrary p-adic parameter values. |
| Weighted nonlinear lifting | Written proof in §§3–4 | Formalize p-adic Taylor estimates, bounded inverse loss, complete-ball iteration, and precision retention. |
| Prescribed-parameter obstruction | Equation (14) follows from checked ingredients | Add the split-parameter cokernel interface and compatible iteration criteria. |
| General singular deformation problems | Not settled by this criterion | Handle rationally rank-deficient Jacobians, changing ranks, higher obstructions, and their compatible branches. |

The efficient formalization order is square uniqueness, coefficient stability, parameter charts, then the weighted nonlinear theorem. Existing unit-Jacobian count and limit APIs should be reused before introducing general matrix analysis.

The other Paper IX questions remain as recorded in the tower release: native presentation invariance and global/completed descent, remaining historical edge identities, exact higher differences, least periods beyond \(N=4\), general Mahler-kernel valuations, arbitrary-row exact tails, and consolidation into one current manuscript. This note does not claim that local perturbations solve those global or valuation problems.

## Source and verification record

- `Universal_Seed_Lifting.tex`: File Service `file_00000000202081f7bfec01bd27e92f85`; read returned lines 1–420, including the complete nonsingular Hensel proof. The remaining file was not audited here.
- `Seed_Lifting.pdf`: File Service `file_00000000cac081f5abc17af90c1163fd`; read pp. 1–14, including Theorems 5.1, 6.1, and 7.1. The later global arithmetic claims were not used or audited.
- `Projector_Resolved_Seed_Calculus_X.pdf`: File Service `file_0000000000ec81f5a0cca9c7d3ea6d93`; read pp. 7–10. Only the conditional packet-decomposition statement is used for context.
- Current implementation: `polynomial_towers/formalization/PolynomialPadicLift.lean`, `PolynomialTaylor.lean`, and the finite-fiber/count modules. Existing tower verification: 22 gates and 127 declaration audits passed in the prior release. No new Lean verification is asserted for this note.
- The new arguments use only integral polynomial identities, matrix valuation bounds, and an explicitly described Cauchy iteration in complete p-adic balls. No claim of mathematical novelty is made.
- Independent proof audit: §§1–6 were read and the polynomial lifting, coefficient perturbation, first-order remainder, and parameter stability arguments passed. The requested explicit types and step scaling in §6 have been added. Source attribution was checked by the authoring session; the independent auditor did not reread the earlier source files. Final proofreading covered this note only. No Lean compilation was performed for these new written statements.
