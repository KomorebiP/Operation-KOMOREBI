# Continuation 113: a literal arithmetic dictionary and its quadratic tame lift

Date checked: 2026-10-01 UTC. This report extends the immutable continuation 112
base, whose ZIP SHA-256 is
`4df3bff07c05985e302d5e9f4104de8f6374c17ca695b1e2e451432572272ae5`.

**Result.** An explicit minimal simple character over
\(F=\mathbf Q_3(\zeta_3)\), with parameter
\(E=\mathbf Q_3(\zeta_9)\) and \(\beta=(\zeta_9-1)^{-10}\), has been
constructed on its actual arithmetic group. Its actual symplectic quotient is
\(\mathbf F_3^3/\operatorname{diag}\mathbf F_3\), with the cyclic alternating
form below, and its Heisenberg representation has degree 3. Its unramified
quadratic tame lift has quotient
\(\mathbf F_9^3/\operatorname{diag}\mathbf F_9\) and Heisenberg degree 9.
The actual canonical extension under the order-two field automorphism has
trace \(-3\). The fixed character is \(\theta_F^2\), not \(\theta_F\).

This is an ordinary source-supported arithmetic instance and a finite exact
computation audit. It is not a Lean formalization of local fields, a proof that
the corresponding automorphic induction contains this type, or an attachment
of the original Paper XI packet or its prescribed \(\kappa\).

## 1. Sources and scope

The authorized project-local primary sources were used. No external search or
new source acquisition was needed.

| Source | Exact result used | Role |
|---|---|---|
| Bushnell–Kutzko, *The admissible dual of GL(N) via compact open subgroups*, Annals of Mathematics Studies 129 (1993) | Definition 1.4.14 and Proposition 1.4.15, p. 41 | Minimality of \(\beta\). |
| Same | Definitions 3.1.7–3.1.8, pp. 90–91 | Literal minimal-stratum H/J groups. |
| Same | Definition 3.2.1 and Proposition 3.2.5, pp. 98–100 | Construction and extension of the actual simple character. |
| Same | Theorem 3.4.1, p. 115; Proposition 5.1.1, p. 158 | Nondegeneracy, unique actual Heisenberg representation, degree. |
| Bushnell–Henniart, *Local tame lifting for GL(N). I: simple characters*, Publ. Math. IHÉS 83 (1996), 105–233 | Corollary 10.16, formulas 10.17–10.18, pp. 170–171; Proposition 11.2, pp. 172–174 | Actual common realization and transferred character. |
| Same | Proposition 11.4, Lemma 11.5, Corollary 11.6, pp. 175–177 | Literal H/J intersections and fixed groups under the arithmetic embedding. |
| Same | Theorem 12.6, pp. 183–184 | Character norm compatibility, consistent with the explicit square restriction. |
| Bushnell–Henniart, *Local tame lifting for GL(N). II: wildly ramified supercuspidals*, Astérisque 254 (1999) | Appendix A2.2–A2.4, p. 100; Remark A2.5, p. 101 | Glauberman correspondent, canonical determinant-one extension and trace sign. |

Source pins:

- BK PDF: `811693b94c03fcbc2cfe33955bc5a00b0fc0b5645ca343f8cc1a3c6511de9c73`.
- BK extracted text: `d69db0827256707a34cd2562af68b9de11fc889ab3f43535ec47b620d58ca9c8`.
- BH1996 PDF: `349c45d24544a1bfc3608678713909594c6a905e2a2ea61d8c170a17dfbb1876`.
- BH1999 PDF: `8d93beb89572055a752b2f63f1f70b8de30403942a37ccc1de4abee28170032a`.

Classification: the source theorems are classical. The explicit dictionary and
trace-sign calculation here are applications and elementary consequences, with
no novelty claim.

## 2. Fields, normalization and the actual hereditary order

Put
\[
 t=\zeta_3-1,\qquad \pi=\zeta_9-1,\qquad
 F=\mathbf Q_3(\zeta_3),\qquad E=\mathbf Q_3(\zeta_9).
\]
Then
\[
 t^2+3t+3=0,\qquad
 \pi^3+3\pi^2+3\pi-t=0.
\]
The latter polynomial is Eisenstein over \(F\): its constant term has
\(F\)-valuation 1 and its other nonleading coefficients have valuation 2.
Thus \(E/F\) is totally ramified of degree 3, with residue field
\(\mathbf F_3\). It is cyclic because it is the cyclotomic extension obtained
by adjoining a cube root of \(\zeta_3\). We normalize \(v_F(t)=v_E(\pi)=1\),
so \(v_F(3)=2\) and \(v_E(3)=6\).

Let \(\psi_{\mathbf Q_3}\) be the usual additive character trivial on
\(\mathbf Z_3\), taking \(1/3\) to \(e^{2\pi i/3}\). Fix
\[
 \psi_F(x)=\psi_{\mathbf Q_3}\left(-\operatorname{Tr}_{F/\mathbf Q_3}(x)/3\right).
\]
It is trivial on \(t\mathcal O_F\), nontrivial on \(\mathcal O_F\), and its
residue character is \(\bar x\mapsto\zeta_3^{\bar x}\). For example,
\(-\operatorname{Tr}(1)/3=-2/3\) and
\(-\operatorname{Tr}(t)/3=1\).

Distinguish the ambient algebra \(A=\operatorname{End}_F(E)\) from its
principal hereditary order
\[
 \mathfrak A=\{a\in A:a\pi^r\mathcal O_E\subseteq\pi^r\mathcal O_E
                    \text{ for every }r\in\mathbf Z\}.
\]
Its radical is \(\mathfrak P\). In the ordered basis \((1,\pi,\pi^2)\),
\[
 (\mathfrak P^r)_{ij}=t^{\lceil(r+j-i)/3\rceil}\mathcal O_F,
 \qquad 0\leq i,j\leq2.
\]
This follows by writing the three successive lattices as
\(\mathcal O_F\oplus\mathcal O_F\pi\oplus\mathcal O_F\pi^2\),
\(t\mathcal O_F\oplus\mathcal O_F\pi\oplus\mathcal O_F\pi^2\), and
\(t\mathcal O_F\oplus t\mathcal O_F\pi\oplus\mathcal O_F\pi^2\).
They repeat after multiplication by \(t\). In particular,
\(\mathfrak P^r\cap E=\pi^r\mathcal O_E\), and
\[
 \operatorname{tr}_{A/F}(\mathfrak P^r)
       \subseteq t^{\lceil r/3\rceil}\mathcal O_F.
\]
Write \(U_{\mathfrak A}^r=1+\mathfrak P^r\) and
\(U_E^r=1+\pi^r\mathcal O_E\) for positive \(r\).

The matrix of multiplication by \(\pi\) is
\[
 \Pi=\begin{pmatrix}0&0&t\\1&0&-3\\0&1&-3\end{pmatrix},
 \qquad
 \Pi_0=\begin{pmatrix}0&0&t\\1&0&0\\0&1&0\end{pmatrix}.
\]
The exact inclusion \(\Pi-\Pi_0\in\mathfrak P^5\) explains why the leading
graded action is a cyclic permutation even though the field extension is
wildly ramified. This is a statement about the associated graded algebra,
not an assertion that the two matrices or fields are equal.

## 3. The actual level-10 simple character

Set \(\beta=\pi^{-10}\). Its valuation is coprime to \(e(E/F)=3\), and the
residue-field condition in BK 1.4.14 is automatic because the residue extension
is trivial. It generates \(E\): an element of \(F\) has \(E\)-valuation
divisible by 3. Thus \([\mathfrak A,10,0,\beta]\) is a minimal simple stratum.

Put \(\psi_E=\psi_F\circ\operatorname{Tr}_{E/F}\). The relative different
has exponent 6. Indeed the derivative at \(\pi\) of its Eisenstein polynomial
is \(3(1+\pi)^2\), of \(E\)-valuation 6, and \(\mathcal O_E=\mathcal O_F[\pi]\).
Consequently \(\psi_E\) is trivial on \(\pi^{-3}\mathcal O_E\) and is not
trivial on \(\pi^{-4}\mathcal O_E\).

Define the character used in the parallel arithmetic route by
\[
 \chi(\pi)=\chi(-1)=1,\qquad
 \chi(u)=\psi_E(\beta\log u)\quad(u\in U_E^1).
\]
The logarithm converges on \(U_E^1\) and is a homomorphism there. This defines
a smooth character of \(E^\times=\langle\pi\rangle\times\{\pm1\}\times U_E^1\).
On \(U_E^4\), logarithm and exponential give inverse isomorphisms with
\(\pi^4\mathcal O_E\). It follows that \(\chi\) has conductor exponent 7.

For \(z\in\pi^6\mathcal O_E\), the logarithm error
\(\log(1+z)-z\) belongs to \(\pi^{12}\mathcal O_E\). This also accounts for
denominators in the logarithm series: for every \(k\ge2\),
\(6k-6v_3(k)\ge12\). Hence
\[
 \chi(1+z)=\psi_E(\beta z)\qquad(z\in\pi^6\mathcal O_E).
\]

The literal BK groups are
\[
 H_F^1=U_E^1U_{\mathfrak A}^6,
 \qquad J_F^1=U_E^1U_{\mathfrak A}^5.
\]
Define
\[
 \theta_F(uv)=\chi(u)\,
 \psi_F\bigl(\operatorname{tr}_{A/F}(\beta(v-1))\bigr),
 \quad u\in U_E^1,\ v\in U_{\mathfrak A}^6.
\]
This formula is well-defined, not a postulated existence condition:

1. The intersection is \(U_E^6\), where the two displayed characters agree by
   the logarithm calculation.
2. The second factor is a character. Its multiplicative error has argument in
   \(\beta\mathfrak P^{12}=\mathfrak P^2\), whose matrix trace is in
   \(t\mathcal O_F\).
3. Conjugation by \(U_E^1\) preserves that factor since it commutes with
   \(\beta\) and matrix trace is cyclic.

The minimal-character definition BK 3.2.1 now shows
\(\theta_F\in\mathcal C(\mathfrak A,0,\beta)\), with its literal restrictions
\(\theta_F|_{U_E^1}=\chi|_{U_E^1}\) and
\(\theta_F|_{U_{\mathfrak A}^6}=\psi_\beta\).

As an independent check of the arithmetic-route input, if \(\sigma\) generates
\(\operatorname{Gal}(E/F)\), then
\(v_E(\sigma\pi/\pi-1)=2\). Since 10 is prime to 3,
\(v_E(\sigma\beta-\beta)=-8\). Applying the same logarithm isomorphism on
\(U_E^4\) gives conductor exponent 5 for \(\chi^\sigma/\chi\), independent
of which inverse convention is used for conjugation. This check does not
establish automorphic-induction type occurrence.

## 4. Literal quotient and commutator coordinates

There are actual group and additive identifications
\[
 J_F^1/H_F^1
 \simeq U_{\mathfrak A}^5/(U_{\mathfrak A}^6U_E^5)
 \simeq \mathfrak P^5/(\mathfrak P^6+\pi^5\mathcal O_E)
 \simeq\mathbf F_3^3/\operatorname{diag}\mathbf F_3.
\]
The first uses the actual intersections with \(E\). The second uses
\(\mathfrak P^{10}\subset\mathfrak P^6\); the action of \(U_E^1\) on this
graded quotient is trivial because commutators raise the grade. For the last,
represent a vector \(x=(x_0,x_1,x_2)\) by
\(X=D(x)\Pi^5\), with \(D(x)\) diagonal and entries lifting the residue
coordinates. The image of \(\pi^5\mathcal O_E\) is the diagonal line.

Use the group-commutator convention \([g,h]=ghg^{-1}h^{-1}\). For
\(X,Y\in\mathfrak P^5\), its leading term is \(XY-YX\) modulo
\(\mathfrak P^{15}\), and \(\psi_\beta\) is trivial on
\(1+\mathfrak P^{15}\). Cyclicity of matrix trace and the leading cyclic action
of \(\Pi\) give
\[
 \theta_F([1+X,1+Y])=\zeta_3^{B(x,y)},\qquad
 B(x,y)=\sum_{i\in\mathbf Z/3\mathbf Z}
            (x_i y_{i+1}-y_i x_{i+1}).
\]
One can see the exponent directly by reducing
\(\operatorname{tr}(\Pi^{-10}[D(x)\Pi^5,D(y)\Pi^5])\) modulo \(t\).
The nine basis-pair values were also computed with the actual matrix \(\Pi\)
over the exact field \(\mathbf Q[t]/(t^2+3t+3)\), without replacing it by
\(\Pi_0\). The resulting matrix is
\[
 \begin{pmatrix}0&1&2\\2&0&1\\1&2&0\end{pmatrix}.
\]
Its radical is exactly the diagonal line. Thus the quotient has order 9 and
the unique actual Heisenberg representation \(\eta_F\) containing
\(\theta_F\) has degree 3, by BK 5.1.1.

For a separate low-level sign check, \(\beta_2=\pi^{-2}\) gives
\(H^1=U_E^1U_{\mathfrak A}^2\), \(J^1=U_{\mathfrak A}^1\), and the same
quotient with the opposite cyclic form in the same coordinate convention.
The character can be chosen trivial on \(U_E^1\), since
\(\operatorname{Tr}_{E/F}(\mathcal O_E)\subseteq t\mathcal O_F\).
This control instance is not substituted for the level-10 character.

## 5. Actual unramified quadratic tame lift

Let \(K=F(i)\), \(i^2=-1\), and \(M=EK\). Since \(X^2+1\) is irreducible
over \(\mathbf F_3\), \(K/F\) and \(M/E\) are unramified quadratic
extensions. Write \(\tau\) for the nontrivial automorphism of \(K/F\),
extended to \(M\) by fixing \(E\). Thus \(\tau(i)=-i\), \(\tau(\pi)=\pi\),
and its residue action is \(x\mapsto x^3\) on \(\mathbf F_9\).

Scalar extension of the lattice chain gives the order \(\mathfrak A_K\) in
\(\operatorname{End}_K(M)\), with radical \(\mathfrak P_K\) and exactly the
same matrix valuation formula, now with entries in \(K\). Put
\[
 \psi_K=\psi_F\circ\operatorname{Tr}_{K/F},\qquad
 \chi_K=\chi\circ N_{M/E}.
\]
The trace identity for the logarithm gives
\(\chi_K(u)=\psi_F(\operatorname{Tr}_{M/F}(\beta\log u))\) on \(U_M^1\).
The same explicit construction therefore yields
\[
 H_K^1=U_M^1U_{\mathfrak A_K}^6,\qquad
 J_K^1=U_M^1U_{\mathfrak A_K}^5,
\]
\[
 \theta_K(uv)=\chi_K(u)
   \psi_K\bigl(\operatorname{tr}_{\operatorname{End}_K(M)/K}(\beta(v-1))\bigr).
\]

This is the standard arithmetic lift of this particular simple character.
To check the identification, realize \(M\) as a two-dimensional \(E\)-space
with chain basis \((1,i)\). The transferred simple character in
\(\operatorname{End}_F(M)\) restricts on the \(E\)-centralizer to
\(\chi\circ\det_E\) and on the deeper congruence subgroup to the matrix-trace
character. Its restriction to \(M^\times\) is consequently
\(\chi\circ N_{M/E}\), while restriction of its matrix trace to the
\(K\)-centralizer is \(\psi_K\circ\operatorname{tr}_K\). These are the two
defining restrictions above. The common realization and restriction are
precisely BH1996 10.16, 11.2; this is not an identification inferred from a
matching dimension.

Under the literal scalar-extension embedding, BH1996 11.4–11.6 give
\[
 (H_K^1)^\tau=H_F^1,\qquad (J_K^1)^\tau=J_F^1.
\]
Here they also follow from the explicit scalar-extended lattices. On the
embedded fixed group, the norm and trace both introduce the degree 2:
\[
 \boxed{\quad \theta_K|_{H_F^1}=\theta_F^2.\quad}
\]
For \(u\in U_E^1\), this says \(N_{M/E}(u)=u^2\); for
\(v\in U_{\mathfrak A}^6\), it says that the \(K/F\) trace of its
\(F\)-valued matrix trace is twice that trace. The construction does not
silently change \(\psi_K\) to a rescaled additive character.

The lifted quotient is literally
\[
 J_K^1/H_K^1\simeq\mathbf F_9^3/\operatorname{diag}\mathbf F_9,
\]
with central commutator
\[
 (x,y)\longmapsto
 \zeta_3^{\operatorname{Tr}_{\mathbf F_9/\mathbf F_3} B(x,y)}.
\]
Its radical before quotienting is the diagonal \(\mathbf F_9\), its quotient
has order 81, and \(\dim\eta_K=9\). The fixed quotient has order 9. On the
embedded \(\mathbf F_3\) quotient the pairing is \(2B\), in agreement with
\(\theta_F^2\).

## 6. An actual canonical-extension sign

This sign can be obtained for the arithmetic representation itself, without
assuming an equivariant comparison with an abstract Schrödinger model.

First, \(\theta_K\) is \(\tau\)-invariant from its norm/trace definition.
The uniqueness of \(\eta_K\) implies \(\eta_K^\tau\simeq\eta_K\).
Moreover \(U_{\mathfrak A_K}^{11}\subseteq\ker\eta_K\), because this group is
contained in \(H_K^1\) and \(\beta\mathfrak P_K^{11}=\mathfrak P_K\) has
matrix trace in \(t\mathcal O_K\). Hence the action factors through the finite
3-group
\[
 G=J_K^1/U_{\mathfrak A_K}^{11}.
\]
The \(\tau\)-fixed subgroup of this finite quotient is the image of \(J_F^1\).
For a direct lifting argument, write \(J_K^1=1+\mathfrak j_K\), where
\(\mathfrak j_K=\pi\mathcal O_M+\mathfrak P_K^5\). If a coset of \(1+x\)
is fixed modulo \(\mathfrak P_K^{11}\), then
\((x+\tau x)/2\in\mathfrak j_K^\tau\) is a fixed representative of that coset.
Division by 2 is legitimate on these integral lattices. This avoids an assumed
fixed-point-surjectivity condition.

Let \(\eta_{F,2}\) be the unique irreducible representation of \(J_F^1\)
containing \(\theta_F^2\). It has degree 3 because the central commutator is
the nondegenerate form \(2B\). Complete reducibility in the finite quotient
and the scalar action of \(H_F^1\) give the actual restriction identity
\[
 \eta_K|_{J_F^1}\simeq\eta_{F,2}^{\oplus3}.
\]
The multiplicity 3 is odd, so BH1999 A2.2 identifies \(\eta_{F,2}\) as the
Glauberman correspondent for the group of order 2.

By A2.3 there is a unique extension \(\widehat\eta_K\) to
\(\langle\tau\rangle\ltimes J_K^1\) satisfying
\(\det\widehat\eta_K(\tau)=1\). By A2.4 its trace at \(\tau\) is either
\(+3\) or \(-3\). Since \(\widehat\eta_K(\tau)^2=1\), trace \(+3\) in
dimension 9 would mean six \(+1\)-eigenvalues and three \(-1\)-eigenvalues,
contradicting determinant 1. Therefore
\[
 \boxed{\operatorname{tr}\widehat\eta_K(\tau)=-3,\qquad
        \operatorname{tr}\widehat\eta_K(\tau j)
            =-\operatorname{tr}\eta_{F,2}(j)\quad(j\in J_F^1).}
\]
The \(+1\) and \(-1\) eigenspaces of \(\widehat\eta_K(\tau)\) have dimensions
3 and 6. This is a restricted ordinary corollary of the cited finite-group
results applied to the actual arithmetic quotient. It does not identify this
extension with the original Paper XI \(\kappa\), nor with a beta-extension to
a larger normalizer.

The automorphism here is the semilinear field automorphism \(\tau\). It is not
the inner conjugation action of \(K^\times\) on \(\operatorname{End}_K(M)\),
which is trivial on scalar \(K\). These actions must not be conflated.

## 7. Computation contract and results

Code: `evidence/lattice/check_lattice113.py`.
Contract: `evidence/lattice/contract113.json`.
Bounded-run provenance and raw outputs: `evidence/lattice/run113/`.

The computation uses exact rational arithmetic in
\(\mathbf Q[t]/(t^2+3t+3)\), and exact \(\mathbf F_3\) and
\(\mathbf F_9=\mathbf F_3[i]/(i^2+1)\) arithmetic. It checks:

- The exact companion-matrix inverse and the grade-5 perturbation of the cyclic
  companion matrix.
- All nine basis-pair matrix traces at critical grades 1 and 5. By bilinearity
  these verify the whole displayed residue matrix in each case.
- All 729 base-field pairing comparisons and all 531,441 ordered pairs of
  \(\mathbf F_9^3\) for alternating symmetry and Frobenius invariance.
- The radicals against a full six-element \(\mathbf F_3\)-basis, quotient
  orders 9 and 81, fixed quotient order 9, and the restriction multiplier 2.

The source-supported arguments above establish the reduction from actual
arithmetic groups to those finite assertions. The computation independently
checks the signs and arithmetic of the resulting formulas. It cannot decide
automorphic-induction occurrence or the original packet attachment.

## 8. Boundary and corrections retained

1. The ambient endomorphism algebra and the hereditary order were separated.
   Writing the order as all of \(\operatorname{End}_F(E)\) would be incorrect.
2. The level-2 proposal was valid, but the main dictionary was moved to the
   actual level-10 character shared with the automorphic-induction route.
   Its critical grade is 5, and its cyclic pairing has the opposite sign from
   the grade-1 control in the fixed matrix convention.
3. Tame lifting yields the power relation \(\theta_K|_{H_F^1}=\theta_F^2\).
   Identifying the fixed representation with \(\eta_F\) without this power
   correction would be false under the displayed normalization.
4. A Weil representation of dimension 3 remains of dimension 3 after
   restriction to \(W_K\). The actual Heisenberg representations of the
   simple types have dimensions 3 over \(F\) and 9 over \(K\). Their dimensions
   measure different objects. The degree-9 lift is not a rank-9 Weil parameter.
5. The cyclic wild automorphic induction of \(\chi\), the explicit arithmetic
   type, and their conductor agreement can coexist without a proved occurrence
   theorem. That remaining implication is delegated to the arithmetic route
   and is not asserted here.
6. Nothing in this example removes continuation 112's obstruction to realizing
   an arbitrary whole tensor packet as one maximal simple Heisenberg quotient.
   No original H5 witness or prescribed \(\kappa\)-comparison is produced.

Self-review: all displayed field, group, character and automorphism notation in
this report was checked for consistency after drafting. The changes from the
initial level-2 task are substantive developments listed above, not silent
proofreading corrections. No theorem-count promotion is made.
