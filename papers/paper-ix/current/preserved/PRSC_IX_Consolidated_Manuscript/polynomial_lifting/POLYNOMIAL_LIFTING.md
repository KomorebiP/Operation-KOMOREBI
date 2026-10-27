# Paper IX: finite polynomial lifting and shared corrections

**Author: Komorebi P. — 8 September 2026.**

This block supplies the actual nonlinear Taylor argument previously missing from the Lean formalization. The statements concern a fixed finite list of integer polynomials. They hold for every positive integer modulus, including composite moduli and modulus one. No Jacobian-surjectivity assumption is needed.

## Statement and notation

Let
\[
F=(F_1,\ldots,F_e)\in\mathbb Z[X_1,\ldots,X_d]^e,
\quad q\ge1,\quad L\ge1,
\quad x\in\mathbb Z^d,
\quad F(x)\equiv0\pmod{q^L}.
\]
Write \(R_q=\mathbb Z/q\mathbb Z\), let \(\rho_q\) denote coordinatewise reduction, and put
\[
r_x=F(x)/q^L\in\mathbb Z^e,
\qquad A_x=DF(x):\mathbb Z^d\longrightarrow\mathbb Z^e,
\qquad J_x=\rho_q\circ A_x.
\]
Here \(A_x\) is computed from the actual formal partial derivatives of the input polynomials. The Lean map \(J_x\) has domain \(\mathbb Z^d\) and codomain \(R_q^e\), viewed as integer modules. It factors through reduction to \(R_q^d\); the cokernel below is presented directly using its integer-domain image.

Define the finite obstruction module and its distinguished class by
\[
\mathcal O_x=R_q^e/\operatorname{im}J_x,
\qquad o_x=[\rho_q(r_x)]\in\mathcal O_x.
\]
The checked criterion is
\[
\boxed{
 o_x=0
 \iff
 \exists y\in\mathbb Z^d:\quad
 y\equiv x\pmod{q^L},\qquad F(y)\equiv0\pmod{q^{L+1}}.
}
\]
The residual exists by the lower congruence and is unique because \(q>0\). The quotient is finite since its ambient module \(R_q^e\) is finite. The theorem permits zero variables or zero equations as well.

## The checked Taylor bridge

For every \(P\in\mathbb Z[X_1,\ldots,X_d]\), integer \(a\), and \(x,t\in\mathbb Z^d\), Lean proves
\[
\boxed{
 a^2\mid P(x+at)-P(x)-a\sum_{i=1}^{d}(\partial_iP)(x)t_i.
}
\]
The proof uses polynomial induction: constants, addition, and multiplication by a variable. The product rule for the actual partial derivatives controls the multiplication step. It does not assume a Taylor identity or a liftability condition.

Taking \(a=q^L\), the inequality \(2L\ge L+1\) gives
\[
F(x+q^Lt)\equiv q^L(r_x+A_xt)\pmod{q^{L+1}}.
\]
Since \(q^L\ne0\) in the integers, cancellation in divisibility yields
\[
F(x+q^Lt)\equiv0\pmod{q^{L+1}}
\iff \rho_q(r_x)+J_xt=0.
\]
Every integer representative of the lower residue has the form \(x+q^Lt\), and this correction equation has a solution exactly when \(o_x=0\).

The positive-depth hypothesis is necessary for the general nonlinear theorem. For \(F(X)=X^2-1\), \(q=2\), \(L=0\), \(x=0\), the Jacobian is zero and the residual class is nonzero, yet \(y=1\) is a solution modulo two in the same residue modulo one. Affine systems retain the previously checked \(L\ge0\) theorem.

## Independence of the integer representative

Suppose \(x'=x+q^Ls\) represents the same lower residue, with exact residual \(r_{x'}\). Polynomial evaluation respects coordinatewise congruences, including when applied to each partial derivative. Hence
\[
J_{x'}=J_x,
\qquad
\rho_q(r_{x'})=\rho_q(r_x)+J_xs.
\]
The two cokernels therefore have the same ambient module and the same defining submodule, and
\[
[\rho_q(r_{x'})]=[\rho_q(r_x)].
\]
Lean states this using one explicit common reduced map, avoiding an implicit comparison between differently indexed quotient types. This establishes independence of the integer representative within the fixed polynomial presentation.

Changing the polynomial presentation is a separate question. Appending a zero equation can change the raw cokernel by adding a copy of \(R_q\), even though it does not change the solutions.

## Two polynomial blocks and one shared lift

Let \(G\in\mathbb Z[X_1,\ldots,X_d]^f\) be a second fixed system with the same variables and the same lower root \(x\). Let \(K_x=\rho_q\circ DG(x)\), and define
\[
\mathcal C_x=\mathbb Z^d/(\ker J_x+\ker K_x).
\]
This quotient is finite: it is a quotient of the finite image of \(J_x\), or equivalently of the finite image of \(K_x\).

Suppose \(u,v\in\mathbb Z^d\) are separately valid corrections:
\[
F(x+q^Lu)\equiv0\pmod{q^{L+1}},
\qquad
G(x+q^Lv)\equiv0\pmod{q^{L+1}}.
\]
Then
\[
\boxed{
[u]=[v]\text{ in }\mathcal C_x
\iff
\exists y\equiv x\pmod{q^L}:\quad
F(y)\equiv0\pmod{q^{L+1}},\quad G(y)\equiv0\pmod{q^{L+1}}.
}
\]
The labels are independent of the choices of valid \(u\) and \(v\). An unconditional version asks for separately valid corrections with equal labels; it does not assume that each block is liftable.

Taylor transport turns a common correction \(t\) into the simultaneous equations \(J_xt=J_xu\) and \(K_xt=K_xv\). The previously checked common-quotient theorem gives precisely the displayed equivalence. Separate solvability alone does not imply joint solvability; the controls include \(F(X)=X\), \(G(X)=X-2\), starting at \(x=0\) modulo two and lifting to modulus four.

## Scope of the completed block

The active Lean sources are in `formalization/`. `PolynomialTaylor`, `PolynomialObstruction`, `PolynomialRepresentative` and `PolynomialShared` contain the new general results. `PolynomialControls` records boundary examples. The affine cokernel and common-quotient dependencies are copied byte-for-byte from their checked sources and freshly compiled by this block's verifier.

The exact contract sources expand the main statements independently of the prose. The verification record gives the final module inventory, axiom closures, negative controls, toolchain pins, source and log hashes, and observed run status. Failed development attempts are preserved separately from the final gate.

For prime \(q=p\), the cokernel is the familiar Jacobian cokernel over \(\mathbb F_p\). The following further formalizations remain: the explicit correction-digit torsor, the prime-field counts \(p^{d-\operatorname{rank}\overline A_x}\) and \(p^{e-\operatorname{rank}\overline A_x}\), where \(\overline A_x:\mathbb F_p^d\to\mathbb F_p^e\) is the induced Jacobian, and compatibility through a specified tower of levels. The finite criterion itself does not construct an infinite lift. For example, \(X^2-5\) lifts from modulus two to four but has no root modulo eight.

The unrestricted native conjectures still require definitions of the objects, allowed presentation changes, transition maps and descent conditions. This block closes the fixed-presentation polynomial Taylor/obstruction and one-step shared-lifting tasks. It does not claim those broader conjectures, a new external priority result, or exact general higher-difference valuations.
