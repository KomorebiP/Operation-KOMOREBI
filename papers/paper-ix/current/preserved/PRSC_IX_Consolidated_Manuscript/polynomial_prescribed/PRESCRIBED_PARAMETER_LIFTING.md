# Paper IX: prescribed-parameter polynomial lifting

**Komorebi P. — 8 September 2026.**

## Setup and exact lift set

Let \(q>0\), \(L\ge1\), and \(m,k,e\ge0\). Write \(S=\mathbb Z/q\mathbb Z\).
Let
\[
F\in\mathbb Z[Y_1,\ldots,Y_m,T_1,\ldots,T_k]^e,
\qquad x=(y_0,t_0)\in\mathbb Z^{m+k},
\qquad F(x)\equiv0\pmod{q^L}.
\]
The actual lower root supplies the unique integral residual
\[
r=q^{-L}F(x)\in\mathbb Z^e,\qquad \bar r=r\bmod q\in S^e.
\]
Let the actual reduced Jacobian blocks be
\[
J=(D_YF)(x)\bmod q:S^m\to S^e,
\qquad K=(D_TF)(x)\bmod q:S^k\to S^e.
\]
For a prescribed parameter digit \(v\in S^k\), choose its canonical integral
representative \(\widehat v\). Define \(\mathcal L_v\) to be the set of actual
residue vectors \(z\in(\mathbb Z/q^{L+1}\mathbb Z)^{m+k}\) satisfying
\[
z\equiv x\pmod{q^L},\qquad F(z)\equiv0\pmod{q^{L+1}},\qquad
z_T\equiv t_0+q^L\widehat v\pmod{q^{L+1}}.
\]
The formal predicate uses canonical integer representatives for evaluation and
the lower congruence. The previously checked polynomial congruence theorem and
digit-to-residue equivalence establish the actual residue-class interpretation.
Changing an integral representative of a parameter digit by a multiple of \(q\)
does not change its prescribed residue modulo \(q^{L+1}\).

## The obstruction theorem

Define the finite solved-block cokernel and its parameter-dependent class by
\[
\mathcal C_x=S^e/\operatorname{im}J,
\qquad o_x(v)=[\bar r+Kv]\in\mathcal C_x.
\]
Then
\[
\boxed{\mathcal L_v\ne\varnothing\iff o_x(v)=0.}
\]
More precisely, the checked digit-to-lift equivalence is
\[
\boxed{\mathcal L_v\cong\{u\in S^m:Ju=-\bar r-Kv\}.}
\]
It sends a solved digit \(u\) to the actual next residue represented by
\(x+q^L(\widehat u,\widehat v)\). The obstruction depends on the solved block
\(J\), not on the range of the full map \((J\ K)\).

Every nonempty \(\mathcal L_v\) has a checked free and transitive action of
\(\ker J\). The action is defined without choosing a base lift. Choosing one
valid solved digit then gives an explicit bijection \(\mathcal L_v\cong\ker J\).
In particular, for every positive modulus,
\[
o_x(v)=0\quad\Longrightarrow\quad\#\mathcal L_v=\#\ker J.
\]
These results permit composite \(q\), the degenerate modulus \(q=1\), and zero
dimensions. Neither \(J\) nor the full reduced Jacobian is assumed surjective.

## Exact prime-field counts

When \(q=p\) is prime, put \(\rho=\operatorname{rank}_{\mathbb F_p}J\). Then
\[
\boxed{\#\mathcal L_v=
\begin{cases}
p^{m-\rho},&o_x(v)=0,\\
0,&o_x(v)\ne0,
\end{cases}}
\qquad
\boxed{\#\mathcal C_x=p^{e-\rho}.}
\]
The count is of distinct actual residue classes at level \(L+1\). The solved
dimension \(m\), rather than the total number \(m+k\) of variables, appears in
the exponent because the parameter digit is fixed. These rank formulas are
asserted only over prime fields.

The main wrapper assumes only the original lower polynomial congruence. It
constructs one residual \(r\) and supplies the criterion and count uniformly
for every \(v\), together with the exact obstruction cardinality.

## Proof and dependency chain

The actual derivative calculation gives
\[
(DF(x)\bmod q)(u,v)=Ju+Kv.
\]
Taylor expansion at depth \(L\ge1\) makes the quadratic remainder divisible by
\(q^{L+1}\). Therefore the digit \((u,v)\) is a polynomial lifting correction
exactly when
\[
\bar r+Ju+Kv=0.
\]
The quotient class \([\bar r+Kv]\) vanishes exactly when this equation admits
\(u\). This uses additive inverses in the image of \(J\), so the sign agrees
with the actual Taylor equation.

The earlier unrestricted correction-digit equivalence is then restricted to
the predicate that the parameter digit equals \(v\). Taking free coordinates
commutes with forming digit residues, and digit residues are injective in the
digit. Consequently the restricted equivalence enforces exactly the actual
parameter residue condition on \(\mathcal L_v\).

Translation by \(\ker J\) acts freely and transitively on the solved-digit fiber.
Transporting this explicit action through the residue equivalence yields the
torsor on \(\mathcal L_v\). Rank-nullity over \(\mathbb F_p\) then gives the
two displayed cardinalities. No numerical enumeration is used to establish
the general theorem.

## Why the solved block matters

Take \(F(Y,T)=T\), \(q=2\), \(L=1\), and \(x=(0,0)\). The full Jacobian
\((0\ 1)\) is surjective, but \(J=0\). Prescribing \(v=1\) forces \(T\equiv2\pmod4\),
which cannot satisfy \(F=0\pmod4\). Prescribing \(v=0\) gives exactly two lifts,
corresponding to \(Y\equiv0,2\pmod4\).

The Lean controls check this actual polynomial example. Thus full-Jacobian
surjectivity alone does not make every prescribed coordinate choice admissible.
The automatic coordinate selection in the earlier chart theorem is compatible
with this obstruction.

## Formal statement map

| Module | Role |
|---|---|
| `PolynomialPrescribedSystem.lean` | Actual split Jacobian blocks, shifted residual, finite solved-digit fiber, and cokernel class. |
| `PolynomialPrescribedLifts.lean` | Equivalence between the solved-digit fiber and actual polynomial residue lifts with the prescribed parameter residues. |
| `PolynomialPrescribedCounts.lean` | Kernel torsors on digits and actual lifts, kernel equivalence, composite-modulus kernel count, and prime-field rank counts. |
| `PolynomialPrescribedObstruction.lean` | Actual residue-vector existence, finiteness, and lower-root-only wrappers deriving the residual and all parameter criteria/counts. |

Principal entry points include
`Komorebi.PolynomialPrescribedObstruction.finite_prescribed_obstruction`,
`Komorebi.PolynomialPrescribedObstruction.prescribed_residue_exists_iff`, and
`Komorebi.PolynomialPrescribedObstruction.finite_prescribed_lift_count`.
The four new mathematical modules contain 16 theorems, ten definitions, and
three abbreviations. Source hashes, expanded statement contracts, independent
review, development records, and the fresh Lean report accompany this note.

## Scope still open

This closes the one-step prescribed-parameter obstruction and its actual fiber
and count interfaces. It does not assert that a chosen parameter path remains
admissible at every later level, or establish a new compatible infinite tower
theorem with prescribed parameters. Those iteration hypotheses and constructions
remain the next clear formalization target.

The preceding weighted lifting and first-order root-motion theorems remain
included in full. General rationally rank-deficient towers, higher obstructions,
analytic regularity, native presentation invariance and global/completed descent,
and further exact valuation questions retain their separate status.
