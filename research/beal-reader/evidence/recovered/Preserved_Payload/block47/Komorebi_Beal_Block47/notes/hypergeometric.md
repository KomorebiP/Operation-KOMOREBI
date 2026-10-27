# Block47: hypergeometric sections and exact Cartier cancellation at seven

Status: a proved coefficient identity and an externally interpreted reduction stratification. The local no-unramified-subquotient bridge is now proved in the independent audit. Global residual irreducibility requires the separate combined argument, including the new two-adic semistability proof.

## 1. The actual objects and parameter dictionary

Throughout, a hypothetical solution means positive pairwise-coprime integers

\[
 A^3+B^5=C^7.
\]

The dictionary into the signature-(5,p,3) paper is
\((a,b,c,p)=(B,-C,A,7)\), and its motive parameter is

\[
 t_0=-B^5/A^3,\qquad 1-t_0=C^7/A^3.
\]

The relevant motive is
\(\mathcal H^+(t)=\mathcal H((1/3,-1/3),(1/5,-1/5)\mid t)\)
over \(K=\mathbb Q(\sqrt5)\). Its Euler curve is
\(y^{15}=x^2(1-x)^{-8}(1-tx)^8t^{-3}\).
The smooth genus-two model used in Block46, after completing the square, is

\[
 Y^2=f(X),\qquad f(X)=X^6+10BX^3+12AX+5B^2.
\]

These objects are established in Pacetti–Villagra Torcomian, §§2 and 7.1, not newly constructed here. Their finite hypergeometric trace formula is over the cyclotomic field \(\mathbb Q(\zeta_{15})\); passage to \(K\), the Tate normalization, and root choices must be retained. No analytic series below is identified with a mod-seven Galois character merely by its notation. [Primary source, arXiv:2512.17845v1](https://arxiv.org/html/2512.17845v1).

## 2. A useful exact cancellation

**Proposition.** Over \(\mathbb Z[A,B]\), the indicated coefficients of \(f(X)^3\) are

\[
 [X^6]f^3=1575B^4,\quad [X^5]f^3=4320A^2B,\quad
 [X^{13}]f^3=36A,\quad [X^{12}]f^3=315B^2.
\]

**Proof.** The exponent-six contributions are \((6,0,0)\) and \((3,3,0)\), with coefficients \(3\cdot25B^4\) and \(3\cdot100\cdot5B^4\). Exponent five is \((3,1,1)\), giving \(3\cdot10\cdot12^2A^2B\). Exponent thirteen is \((6,6,1)\), giving \(3\cdot12A\). Exponent twelve has \((6,6,0)\) and \((6,3,3)\), giving \((15+300)B^2\). These exhaust the possible triples. ∎

Consequently the coefficient matrix modulo seven is

\[
 \boxed{M=\begin{pmatrix}0&A^2B\\ A&0\end{pmatrix}},
 \qquad M^2=A^3B I_2,\qquad \det M=-A^3B.
\]

Both diagonal lanes cancel identically, while the off-diagonal lanes retain exactly the products shown. This is an actual arithmetic cancellation, not a proposed analogy.

For \(7\nmid C\), Block46's discriminant identity

\[
 \operatorname{disc}(f)=2^{12}3^65^5C^{14}
\]

makes the reduction smooth of genus two. Over \(\mathbb F_7\), in the differential basis \(dX/Y,X\,dX/Y\), \(M\) is the Cartier–Manin matrix with the column convention. The Hasse–Witt matrix is \(M^{\mathsf T}\). Over a perfect extension, coefficient roots and semilinear iterates must be inserted; here all entries lie in the prime field, so ordinary matrix iteration suffices. The coefficient formula and adjoint convention are taken from Achter–Howe §§2.4–2.5 and 3.1. [Primary source](https://www.math.colostate.edu/~achter/math/hwcm0618.pdf).

The stable rank of Cartier gives the following stratification of the good-reduction case:

| Condition | Rank of \(M\) | Rank of \(M^2\) | Reduction information |
|---|---:|---:|---|
| \(7\nmid AB\) | 2 | 2 | Ordinary, 7-rank 2 |
| \(7\mid A\) | 0 | 0 | Cartier zero, 7-rank 0 |
| \(7\mid B\) | 1 | 0 | Nonzero nilpotent Cartier, 7-rank 0 |

The last two rows use pairwise coprimality. If \(7\mid C\), the smooth-matrix interpretation does not apply; this is the separate semistable stratum already studied in Block46.

The zeta congruence is

\[
 L_{\mathbb F_7}(T)\equiv\det(I-MT)=1-A^3BT^2\pmod7,
\]

or, for the degree-four characteristic polynomial of Frobenius,

\[
 \chi_7(T)\equiv T^4-A^3BT^2\pmod7.
\]

The exact computation independently counted points over \(\mathbb F_7\) and \(\mathbb F_{49}=\mathbb F_7[u]/(u^2-3)\) for every smooth residue specialization. There are 42 such pairs \((A,B)\), divided into 30 ordinary, six zero-Cartier and six rank-one nilpotent cases. All satisfy the congruence. The point counts further give \(\#\mathcal C(\mathbb F_7)=8\) for all 42 fibers. When \(B=0\), \(\chi_7(T)=T^4+49\). When \(A=0\), its possible values are \(T^4+7T^2+49\) and \(T^4-14T^2+49\). These last assertions are exhaustive finite checks, not a claim about an unchecked family of residue characteristics.

### The local bridge is now proved; global application is separate

The independent audit `notes/cartier_independent_audit.md` proves: over a finite unramified extension of Q_7, an abelian variety with good reduction and geometric 7-rank zero has no nonzero unramified subquotient of its seven-torsion representation. The proof takes finite-flat closures and quotients, then invokes Raynaud's uniqueness of finite-flat models for absolute ramification index e<7-1. A nontrivial constant generic quotient would have an étale model, contradicting connectedness of the special fiber. The audit treats F_49 coefficients and algebraic-closure constituents by restriction of scalars and powers of the abelian variety. [Raynaud, Theorem 3.3.3 and Corollary 3.3.6(1), printed p.268](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf).

Thus in the two 7-rank-zero strata above, the local Jacobian torsion has no unramified constituent. Relating a stable RM lattice to full J[7] up to semisimplification remains as in Block46.

The odd-C global character argument supplies an unramified constituent at seven under hypothetical reducibility. For even C, its early ramification argument additionally needed control at two. The separate written proof `notes/evenC_semistability_at2.md` supplies semistability there. Applying the local theorem to a globally forced character requires review of this complete dependency chain; the Cartier computation alone is not a global irreducibility theorem.

## 3. The period and its seven coefficient lanes

For the Euler-curve differential \(dX/(Xy)\), formal Euler-integral exponents give the local period proportional to

\[
 t^{1/5}F(t),\qquad F(t)={}_2F_1(8/15,-2/15;7/5;t)
 =\sum_{n\ge0}c_nt^n.
\]

The ordinary real Euler integral is not convergent at both endpoints for these parameters. A Pochhammer cycle or analytic continuation is required for a period interpretation. The following formal-series identities are proved directly from the displayed Pochhammer coefficients and do not depend on analytic convergence.

\[
 c_0=1,\qquad
 \frac{c_{n+1}}{c_n}
 =\frac{(15n+8)(15n-2)}{45(n+1)(5n+7)}.
\]

For \(\theta=t\,d/dt\),

\[
 [\theta(\theta+2/5)-t(\theta+8/15)(\theta-2/15)]F=0.
\]

Set \(F_r(z)=\sum_{n\ge0}c_{7n+r}z^n\) and \(D=z\,d/dz\). Exact reconstruction and the coupled recurrences are

\[
 F(t)=\sum_{r=0}^6t^rF_r(t^7),
\]

\[
 (7D+r)(7D+r+2/5)F_r
 =(7D+r-1+8/15)(7D+r-1-2/15)F_{r-1}\quad(1\le r\le6),
\]

\[
 (7D)(7D+2/5)F_0
 =z(7D+6+8/15)(7D+6-2/15)F_6.
\]

This is a literal instance of the source toolkit's coefficient sections and exact analysis/synthesis. Every \(c_n\) is nonzero, so every lane has nonzero constant coefficient \(c_r\): no analytic coefficient lane disappears identically.

More significantly,

\[
 c_1=-16/315,\qquad v_7(c_1)=-1.
\]

Thus the raw period is not in \(\mathbb Z_7[[t]]\). The worked factorial-lane theorem that obtains unit denominators cannot be transferred to this period without a new integral normalization. A finite valuation scan through index 100000 finds first new minima \((1,-1),(1030,-2),(3431,-3)\). It does not prove unbounded denominators. The scan is a diagnostic showing that multiplying once by seven is not an adequate coefficient normalization even at moderate depth.

A root-of-unity Fourier projector of order seven involves \(1/7\) and is unavailable in characteristic seven. Cartier coefficient sections remain legal over any coefficient ring, but reducing the coefficients first is legal only once their integrality has been established. The Cartier–Manin construction in §2 has integral polynomial input and avoids this failed transfer.

## 4. All unit parameter lanes are locally populated

For any commutative ring and any parameter \(t\), set

\[
 A_t=t^{28}(1-t)^{30},\quad
 B_t=-t^{17}(1-t)^{18},\quad
 C_t=t^{12}(1-t)^{13}.
\]

Direct multiplication proves the polynomial identities

\[
 A_t^3+B_t^5=C_t^7,\qquad B_t^5=-tA_t^3.
\]

Indeed the left side of the first identity factors as
\(t^{84}(1-t)^{90}(1-t)=t^{84}(1-t)^{91}\).
If \(t\) and \(1-t\) are units, then all three bases are units and
\(-B_t^5/A_t^3=t\).

This supplies a local solution for every regular hypergeometric parameter, simultaneously over every finite field, every prime-power quotient, and every local ring where those two elements are units. Increasing the prime-power depth of the parameter partition cannot by itself empty such a lane. This is stronger than a bounded finite-field experiment because the identity is polynomial over \(\mathbb Z\).

It does not prevent exclusion of a fixed global modular candidate. Nor does it construct primitive positive integer solutions. For rational \(t<0\) the displayed bases are positive rationals, but clearing denominators by weighted scaling creates the common-divisor issue that primitivity forbids. That global issue is the retained obstruction.

## 5. Computation contract and replay

Authoritative code: `computations/hypergeometric_audit.py`.
Contract: `computations/hypergeometric_contract.json`.
Audited run: `verification/hypergeometric_run/manifest.json` and `result.json`.

The computation uses Python 3.12.14 standard-library exact arithmetic, no random sampling, no numerical hypergeometric approximation, and no external symbolic package. It verifies the coefficient identity with sparse multivariate multiplication, then checks every specialization with independently implemented dense multiplication and point counts. It also checks 351 rational series coefficients and 417 unit-parameter instances in the declared seven quotient rings. The generic identities are proved above; the finite assertions are precisely bounded in the contract.

Replay from `work47`:

```sh
python3 computations/hypergeometric_audit.py --output computations/hypergeometric_audit.json
```

Failures and boundaries: no execution failure occurred in the recorded run. The attempted transfer of the old unit-denominator normalization fails because the new period's first nonconstant coefficient has a factor seven in its denominator. No primitive solution, residual representation or Hilbert modular form was eliminated by this computation.

Project source material read: `toolkit/block15_section.tex`, especially factorial-residue, polyphase, Cartier and holonomic sections; and `toolkit/From_Factorial_Lanes_to_Padic_Transfer.tex`, including the unit-normalization and refinement boundaries. Their exact section calculus is used as stated. No general claim that every hypergeometric motive inherits the factorial example's divisibility is made.
