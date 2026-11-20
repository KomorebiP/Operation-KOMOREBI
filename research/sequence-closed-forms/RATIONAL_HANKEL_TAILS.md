# Rational Hankel tails, sharp rank, and a common rational kernel

Author: **Komorebi P.**
Checkpoint: **SEQ-DH-2026-11-20-001**.
Status: written proof, exact implementation, and separate self-review.
Historical novelty: unassessed. This note does not claim a new general theory
of banded determinants or finite-state recurrences.

This continues the [finite differential Hankel calculus](FINITE_DIFFERENTIAL_HANKEL.md).
All fields below have characteristic zero. The parameters are fixed while
the determinant size varies.

## 1. Objects and the principal result

Let
\[
 P(m)=\sum_{d=0}^{D}a_d m^{\underline d},\qquad
 \mathcal D=\sum_{k=0}^{r}c_k\partial_x^k
\]
be nonzero, with **actual** degree \(D\) and **actual** order \(r\). Thus
\(a_Dc_r\ne0\). Set \(M=D+r\), and define
\[
 F_P[x^{2m}]=P(m)\binom{2m}{m},\quad F_P[x^{2m+1}]=0,\quad
 L[f]=F_P[\mathcal Df],
\]
\[
 \mu_n=L[x^n],\qquad
 W_N=\det[\mu_{i+j}]_{0\le i,j<N},\qquad W_0=1.
\]

**Theorem A (rational determinant generating functions).** Every such
sequence \(W_N\) has a rational ordinary generating function over the
coefficient field. If \(M\ge1\), put
\[
 w=4M,\qquad s=\binom{2w}{w}=\binom{8M}{4M},\qquad K=2w+1.
\]
There is an explicitly defined \(s\)-dimensional constant matrix \(T\), an
initial vector \(v\), and a coordinate vector \(e\), such that
\[
 \boxed{W_{K+n}=\frac14 e^{\mathsf T}T^n v\quad(n\ge0).}
\]
In particular there is a monic constant-coefficient forward recurrence of
order \(s\), valid from index \(K\). The order can be much smaller, and the
bound is not asserted minimal or computationally efficient.

If either input is zero, \(W_N=0\) for \(N\ge1\). If \(M=0\), writing
\(b=a_0c_0\ne0\) gives
\[
 W_N=b(2b)^{N-1}\quad(N\ge1),\qquad
 \sum_{N\ge0}W_Nz^N=\frac{1-bz}{1-2bz}.
\]

All zero initial minors and all later zero minors are included. There is no
division by a Hankel determinant or by a band coefficient.

## 2. Chebyshev data needed in the proof

Let \(C_n(x)=2T_n(x/2)\), so \(C_0=2\) and \(C_n\) is monic for \(n\ge1\).
Write \(G_{ij}=L[C_iC_j]\). Then
\[
 \det G_N=4W_N\quad(N\ge1).
\]
The factor is 4, not \(4^N\); it comes from the single exceptional leading
coefficient of \(C_0\).

The retained derivative-product formulas give two odd polynomials \(E,O\),
of degree at most \(2M-1\), such that
\[
 L[C_n]=
 \begin{cases} E(n),&n>0\text{ even},\\O(n),&n\text{ odd},\end{cases}
 \qquad L[C_0]=2a_0c_0.
\]
For completeness, their underlying identities are
\[
 F_0[C_n^{(k)}]
 =n(k-1)!\binom{(n+k-2)/2}{k-1}^{\!2}
 \quad(k\ge1,\ n\ge k,\ n\equiv k\pmod2),
\]
and
\[
 F_{d+1}[C_n^{(k)}]
 =\frac{n^2-(k+2d)^2}{4(d+k)}F_d[C_n^{(k)}]\quad(d+k>0).
\]
For \(k=0,d\ge1,n>0\) even,
\[
 F_d[C_n]=\frac{n}{4^{d-1}(d-1)!}
             \prod_{j=1}^{d-1}(n^2-4j^2).
\]
Terms of mismatched parity vanish; \(d=k=0\) contributes zero at positive
index. These formulas follow by integrating the Gegenbauer generating
function against the arcsine functional and then applying the differentiated
Chebyshev equation. Their elementary derivation and endpoint conventions
are retained in the base note and tested independently there.

For integer \(n\), define the polynomial/parity expression
\[
 p(n)=\frac{E(n)+O(n)}2+(-1)^n\frac{E(n)-O(n)}2.
\]
In particular \(p(0)=0\). Define an even sequence
\[
 \tau(n)=
 \begin{cases}p(|n|),&n\ne0,\\2a_0c_0,&n=0.\end{cases}
\]
The exact identity \(C_iC_j=C_{i+j}+C_{|i-j|}\) now gives, including index zero,
\[
 \boxed{G_{ij}=p(i+j)+\tau(i-j)+2a_0c_0\delta_{i0}\delta_{j0}.}       \tag{1}
\]
Thus the polynomial Hankel term, the Toeplitz term, and the exceptional
corner are all explicit.

## 3. The boundary-safe finite-difference congruence

Let
\[
 q_{2j}=(-1)^j\binom{2M}{j}\ (0\le j\le2M),\qquad q_{2j+1}=0,
\]
and put \(q_a=0\) outside \(0\le a\le w=4M\).
Let \(Q_N\) be lower triangular with \((Q_N)_{ij}=q_{i-j}\).
Its diagonal entries are 1. The leading sections of the fixed infinite matrix
\[
 B=QGQ^{\mathsf T}
\]
are therefore exactly \(B_N=Q_NG_NQ_N^{\mathsf T}\), and
\[
 \det B_N=\det G_N.
\]
The finite-difference operator \(\sum_aq_af(n-a)=(1-E_{\mathrm{back}}^2)^{2M}f(n)\)
annihilates every polynomial in \(n\) of degree at most \(2M-1\), separately
on both parities. Hence it annihilates \(p(n)\) for all integers \(n\).

**Lemma B (band and stationary tail).** One has
\[
 B_{ij}=0\quad\text{if }|i-j|>w,
\]
and, for \(i,j\ge w+1\),
\[
 B_{ij}=t_{i-j},\qquad
 t_d=\sum_{a,b=0}^{w}q_aq_b\,\tau(d-a+b).                         \tag{2}
\]
Also \(t_d=0\) for \(|d|>w\).

**Proof.** If \(i>j+w\), the row stencil is complete. For each allowed
column shift \(b\), every \(i-a-j+b\) is positive. The Toeplitz term in (1)
is therefore a polynomial/parity expression in \(i-a\) of degree at most
\(2M-1\), so the complete row difference annihilates it. The same row
difference annihilates the polynomial Hankel term. The transformed corner
has support only on indices at most \(w\), and cannot contribute. Symmetry
gives the other off-band half.

If \(i,j\ge w+1\), both stencils are complete. The Hankel polynomial
vanishes after row differencing, and the corner is absent. What remains
is exactly (2). For \(|d|>w\), all \(d-a+b\) have the same strict sign,
so a complete difference again annihilates the polynomial/parity expression.
This proves the lemma. \(\square\)

The boundary check is essential. Replacing \(2M\) by \(M\) in the stencil
does **not** in general make the whole matrix banded. For \(P=1\) and
\(\mathcal D=1+\partial_x\), that shorter stencil leaves
\(G_{0j}-G_{0,j-2}=4\) at every odd \(j\ge3\). It only kills the distant
interior after differencing both indices. This failed shortcut is retained
as an exact counterexample in the computation record.

Every row \(i\ge K=2w+1\) of \(B\) is now stationary: its potentially nonzero
columns satisfy \(j\ge i-w\ge w+1\), so all its band entries are given by (2).

## 4. Signed matching states: proof of Theorem A

This construction works for any fixed infinite matrix of half-bandwidth \(w\);
its row weights can initially depend on position.

Before processing row \(i\), keep the occupied columns in the sliding window
\([i-w,i+w-1]\). Record them as a \(w\)-element subset
\(S\subset\{0,\ldots,2w-1\}\). Columns left of the window must already be
occupied. Initially, the negative columns \(-w,\ldots,-1\) are treated as
occupied virtual columns. The initial state is
\[
 S_*=\{0,\ldots,w-1\}.
\]
This convention never permits choosing a negative column.

In row \(i\), choose an unoccupied position \(k\in\{0,\ldots,2w\}\), where
\(2w\) is the newly exposed rightmost column. Position 0 must be occupied
after the choice, or it would leave the window unmatched. The next state is
\[
 S'=\{j-1:j\in S\cup\{k\},\ j>0\}.
\]
The transition weight is
\[
 \boxed{(-1)^{|\{j\in S:j>k\}|}\,B_{i,i-w+k}.}                    \tag{3}
\]
The sign counts precisely the new inversions with columns selected in
earlier rows. Earlier columns left of the window are smaller than the
chosen column and do not affect the count; virtual negative columns never
contribute an inversion.

After \(N\) rows, acceptance in state \(S_*\) means that every real column
\(0,\ldots,N-1\) is used once and no larger column is used. Thus accepted
paths are in weight-preserving bijection with determinant permutations,
including their signs. If \(v_N\) is the state vector after \(N\) rows,
\[
 e_{S_*}^{\mathsf T}v_N=\det B_N.
\]
There are \(s=\binom{2w}{w}\) possible states. From row \(K\) onwards,
(3) depends only on \(S,k\), because its matrix entry is \(t_{w-k}\).
Denote this constant transition matrix by \(T\), and put \(v=v_K\).
Then \(v_{K+n}=T^nv\), proving the asserted representation of \(W_{K+n}\).

In particular
\[
 \sum_{N\ge0}W_Nz^N=
 \sum_{N=0}^{K-1}W_Nz^N+
 \frac{z^K}{4}e_{S_*}^{\mathsf T}(I-zT)^{-1}v.                    \tag{4}
\]
The inverse is rational by the adjugate identity, with denominator
\(\det(I-zT)\), whose constant term is 1. Cayley--Hamilton supplies the
stated order-\(s\) monic forward annihilator from index \(K\).
No assumption about nonzero extreme bands or nonsingular leading minors
entered the argument. This proves Theorem A at every specialization.
\(\square\)

## 5. The separated rank bound is always sharp

The leading coefficients of the positive-index odd polynomials are especially
simple. The unique term of total degree \(D+r=M\) comes from \(a_Dc_r\).
Put
\[
 b=\frac{a_Dc_r}{4^{M-1}(M-1)!}\ne0.
\]
If \(r\) is even, the coefficient of \(t^{2M-1}\) in \(E\) is \(b\)
and in \(O\) is zero; if \(r\) is odd, the two roles are reversed.

**Theorem C (sharpness, including an explicit minor).** For \(M\ge1\), every
strictly separated \(2M\)-square Gram block whose row and column sets each
contain \(M\) even and \(M\) odd indices is nonsingular. Consequently
the exact maximum separated rank is \(2M\), and no smaller uniform scalar
generator width can represent all separated blocks of this fixed functional.

Here is a product formula. Let \(I,J\) be the increasing row and column sets,
\(\min I>\max J\ge0\). Let \(\sigma(I)\) be the sign of the permutation
that groups its even indices before its odd indices. For an increasing set
\(A\), write \(\Delta(A^2)=\prod_{i<j,\ i,j\in A}(j^2-i^2)\).
Then
\[
 \boxed{\begin{aligned}
 \det G_{I,J}={}&
 (-1)^{rM}4^M\sigma(I)\sigma(J)b^{2M}
 \left(\prod_{k=0}^{M-1}\binom{2M-1}{2k}\right)^2
 \left(\prod_{i\in I}i\right)\\
 &{}\times
 \Delta(I_{\rm even}^2)\Delta(I_{\rm odd}^2)
 \Delta(J_{\rm even}^2)\Delta(J_{\rm odd}^2).
 \end{aligned}}                                                   \tag{5}
\]
In particular these minors depend only on \(a_Dc_r,D,r\), and the indices,
not on any lower coefficients.

**Proof.** Expand \(E(i+j)+E(i-j)\) and \(O(i+j)+O(i-j)\).
Only even powers \(j^{2k}\) occur. The usual generators factor as
\[
 U_I=[W_I C_+,\ \operatorname{diag}((-1)^i)W_I C_-],\quad
 V_J=[Z_J,\ \operatorname{diag}((-1)^j)Z_J],
\]
where \(W_{ik}=i^{2k+1}\), \(Z_{jk}=j^{2k}\), and \(0\le k<M\).
The polynomial in the \(k\)-th column of \(C_+\) has degree \(2M-1-2k\)
and leading coefficient \(b\binom{2M-1}{2k}\). For \(C_-\) the leading
coefficient is multiplied by \((-1)^r\). Both coefficient matrices are
invertible. Their determinant product is
\[
 (-1)^{rM}b^{2M}
       \left(\prod_{k=0}^{M-1}\binom{2M-1}{2k}\right)^2.
\]
Grouping the two parities in the evaluation matrices and subtracting the
first column block from the second gives the factors
\((-2)^M\), the parity permutation signs, and the Vandermonde determinants
in the squared indices. The odd-power row evaluations additionally give
\(\prod_{i\in I}i\). Taking determinants in \(G_{I,J}=U_IV_J^{\mathsf T}\)
gives (5). Every factor is nonzero in characteristic zero. \(\square\)

For \(M=0\), \(G\) is diagonal and its separated rank is zero.

## 6. Exact branch orders and one common rational kernel

The published moment OGF has the form
\[
 \mathcal M(z)=\sum_{n\ge0}\mu_nz^n
    =\frac{R(z)}{(1-4z^2)^{M+1/2}},\qquad\deg R\le2M.
\]

**Theorem D.** For nonzero inputs its numerator satisfies
\[
 \boxed{R(1/2)=a_Dc_r(1/2)_M,\qquad
 R(-1/2)=(-1)^r a_Dc_r(1/2)_M.}                                  \tag{6}
\]
Thus the two endpoint factors cannot cancel. The moment OGF has algebraic
degree exactly two over the rational-function field, and is parametrized by
\(z=t/(1+t^2)\).

**Proof.** In the base numerator, only the \(d=D\) term survives at
\(z=\pm1/2\), giving \(a_D(1/2)_D\). In the numerator iteration for the
\(k\)-th monomial derivative,
\[
 R_{k+1}=z(1-4z^2)(R_k+zR_k')
              +4(2D+2k+1)z^3R_k,
\]
substitution at \(\pm1/2\) multiplies the value by
\(\pm(D+k+1/2)\). In the final common numerator, every \(k<r\) contribution
has a factor \(1-4z^2\), so only \(c_rR_r\) survives. This proves (6).
The square of the moment OGF has odd pole order \(2M+1\) at both endpoints;
a rational function cannot have a square with such a valuation.
The quadratic equation gives the matching upper degree bound.
\(\square\)

**Theorem E (fixed rational kernel).** Define
\[
 H(t)=(1+t^2)^{2M}R\!\left(\frac{t}{1+t^2}\right).
\]
This is a polynomial of degree at most \(4M\), and for every \(n\ge0\),
\[
 \boxed{\mu_n=[t^n]\frac{H(t)}{(1-t^2)^{2M}}(1+t^2)^n.}           \tag{7}
\]
The amplitude has exact pole order \(2M\) at both \(t=1\) and \(t=-1\)
when \(M>0\). For \(M=0\) the amplitude is the nonzero constant \(a_0c_0\).

To prove (7), take \(u=z(1+u^2)\). Then
\[
 \sqrt{1-4z^2}=\frac{1-u^2}{1+u^2},\qquad
 1-z\,2u=\frac{1-u^2}{1+u^2}.
\]
The classical coefficient-transfer identity
\[
 \sum_{n\ge0}[t^n]A(t)\Phi(t)^n z^n
       =\frac{A(u)}{1-z\Phi'(u)},\quad u=z\Phi(u),
\]
with \(\Phi(t)=1+t^2\), becomes exactly the displayed moment OGF.
This identity also follows directly by a formal change of variable in
the residue of \(A(t)/(t-z\Phi(t))\); its derivative at the simple formal
root is \(1-z\Phi'(u)\). The noncancellation of \(H\) at \(\pm1\) follows
from (6). For this fixed \(\Phi\), the amplitude is unique because the
substitution \(u=z+O(z^2)\) is formally invertible.

This links the newer differential moment families back to the earlier
universal coefficient-transfer calculus with a **single fixed** \(\Phi\).
It is a statement about moments; Theorem A separately treats their Hankel
determinants.

## 7. Implementation and evidence boundaries

The implementation extends the existing differential Hankel module.
It constructs the finite-difference entries and signed transfer directly.
For manageable examples it obtains a recurrence by finding an exact identity
\[
 \sum_j b_j T^jv=0
\]
in the **complete state vector**, then recomputes that residual. This proves
the resulting eventual recurrence for infinitely many indices; matching
finitely many scalar determinants alone would not do so. The certificate
order is an annihilator order, not a minimal observable-order assertion.

The general proof has no state cap. The executable routine defaults to at
most 20,000 explicit states. For \(M=1\) the construction has 70 states;
for \(M=2\), 12,870; for \(M=3\), 2,704,156. This intentionally loose
construction establishes rationality and supplies certificates, while the
retained fixed-width Schur solver is preferable for routine determinant
prefixes. No new worst-case efficiency claim follows.

The standard-library implementation is tools/sequence_rational_hankel.py.
Run tools/verify_sequence_rational_hankel.py with an --output JSON filename
to reproduce the exact moment, minor, banding, and full-state checks.
The companion tools/verify_sequence_linear_hankel.py reproduces the complete
polynomial-identity certificate in the [linear-weight theorem](LINEAR_WEIGHT_RECURRENCE.md).

Read the [separate self-review](RATIONAL_HANKEL_REVIEW.md) and
[bounded literature check](RATIONAL_HANKEL_LITERATURE.md).
These are project checks, not independent review or Lean formalization.
The transfer mechanism has substantial prior literature; no historical-priority
claim follows from this continuation.
