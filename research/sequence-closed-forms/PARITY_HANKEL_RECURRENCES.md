# Parity compression and quadratic Hankel recurrences

Author: Komorebi P.

Checkpoint: SEQ-DH-2026-11-20-002. Base: published revision
f3da1097aa4faacd2c1201b48e015de07ee4b045. Review: project self-review;
historical novelty and independent review are unassessed.

## 1. Definitions and inherited banding

Work over a characteristic-zero field. Define
\[
 F_P[x^{2m}]=P(m)\binom{2m}{m},\qquad F_P[x^{2m+1}]=0,
 \quad L[f]=F_P[\mathcal D f],
\]
where \(P\) is a polynomial and \(\mathcal D\) a finite constant-coefficient
differential operator. Put
\[
 W_N=\det[L[x^{i+j}]]_{0\le i,j<N},\qquad W_0=1.
\]
Use \(C_0=2,C_1=x,C_n=xC_{n-1}-C_{n-2}\). The Chebyshev Gram matrix
\(G_{ij}=L[C_iC_j]\) has \(\det G_N=4W_N\) for \(N\ge1\).

Let \(M=\deg P+\operatorname{ord}\mathcal D\ge1\), with nonzero inputs.
The [preceding rational-Hankel proof](RATIONAL_HANKEL_TAILS.md) supplies the lower triangular congruence
\[
 B=QGQ^{\mathsf T},\qquad Q=(1-E_{\rm back}^{,2})^{2M}.
\]
It preserves every leading determinant, gives half-bandwidth \(4M\), and
has a stationary Toeplitz tail \(B_{ij}=t_{i-j}\) for \(i,j\ge4M+1\).
Every original row \(i\ge8M+1\) is stationary. All statements include
singular leading minors. Zero inputs and \(M=0\) retain the explicit formulas
in the preceding proof.

## 2. The parity reduction

**Theorem G.** Suppose the operator contains only even derivatives. Define
\[
 A_n=\det[B_{2i,2j}]_{0\le i,j<n},\qquad
 B_n^{\rm o}=\det[B_{2i+1,2j+1}]_{0\le i,j<n},
 \quad A_0=B_0^{\rm o}=1.
\]
Then
\[
 W_N=\frac14 A_{\lceil N/2\rceil}B^{\rm o}_{\lfloor N/2\rfloor}
 \quad(N\ge1).                                             \tag{1}
\]
Each block has half-bandwidth \(2M\), and its rows are stationary from
\(K=4M+1\). Each therefore has a signed matching transfer with
\[
 s=\binom{4M}{2M}
\]
states. The two stationary transfer matrices are identical. Consequently an
eventual annihilator for \(W_N\) has order at most \(s(s+1)\), from \(N=2K\).

If the operator contains only odd derivatives, put
\[
 H_n=\det[B_{2i,2j+1}]_{0\le i,j<n},\qquad H_0=1.
\]
Then
\[
 W_{2n+1}=0,\qquad W_{2n}=\frac{(-1)^n}{4}H_n^2\quad(n\ge1). \tag{2}
\]
The cross block has lower bandwidth \(2M\), upper bandwidth \(2M-1\), and
a stationary transfer with \(t=\binom{4M-1}{2M}\) states. An eventual
annihilator for the full sequence has order at most \(t(t+1)\), from \(2K\).

**Proof.** An even operator preserves parity, so the odd moments vanish.
Thus \(G\), and also \(B\), have no entries between opposite parities.
Reordering rows and columns by parity introduces two equal permutation signs,
whose product is one. This proves (1), including zero minors.

For an odd operator the even moments vanish. The reordered even-sized Gram
matrix is \(\left(\begin{smallmatrix}0&H\\H^{\mathsf T}&0\end{smallmatrix}\right)\).
Swapping its two column blocks gives sign \((-1)^n\), so its determinant
is \((-1)^n\det(H)^2\). The odd-sized matrix has rank at most \(2n\).
This proves (2). The factor \(1/4\) applies only at positive full size;
\(W_0=1\) is separate.

In the even case, the full bandwidth condition becomes \(|i-j|\le2M\).
In the odd case, \(2i-(2j+1)\) is odd, so
\(-2M+1\le i-j\le2M\). At block row \(i\ge K\), all corresponding original
row and column indices are at least \(4M+1\), proving stationarity.

For lower and upper bandwidths \(l,u\), the sliding-window matching proof
uses \(l\) occupied positions in a window of length \(l+u\), hence
\(\binom{l+u}{l}\) states. The next-state and inversion-sign argument is
unchanged. In the even case both tails are \(t_{2(i-j)}\), so their transfers
coincide.

Products of two outputs of the same \(s\)-state transfer are outputs of its
symmetric square, of dimension \(s(s+1)/2\). For the odd subsequence in (1),
advance the first initial vector once before taking this symmetric product.
The characteristic polynomial of the symmetric-square transfer therefore
annihilates both subsequences in the block index. Substitution of the square
of the full forward shift gives the stated full-sequence bound. In (2), use
the negative symmetric-square transfer to absorb \((-1)^n\), then interlace
with the zero odd subsequence. No pivot division is used. \(\square\)

At \(M=2\), the block state counts are 70 and 35. The corresponding general
full-sequence bounds are 4,970 and 1,260, compared with the earlier 12,870.
These are annihilator bounds, not minimality claims.

## 3. A uniform quartic for every quadratic weight

Now take the identity operator and falling-basis weight
\[
 P(m)=a+bm+cm(m-1).
\]
The even block sequences in (1) will still be denoted \(A_n,B_n^{\rm o}\).
Define
\[
 \begin{aligned}
 g(X)={}&X^4+(-8a+8b-24c)X^3\\
 &+(24a^2-32ab-96ac+16b^2)X^2\\
 &+(-32a^3+32a^2b-96a^2c)X+16a^4.
 \end{aligned}                                               \tag{3}
\]

**Lemma.** Both block sequences satisfy \(g(S)^4U_n=0\) for every \(n\ge1\),
at every characteristic-zero specialization of \(a,b,c\).

**Complete polynomial certificate.** Fix the degree-two stencil and 70-state
model even when \(c=0\). Its stationary start is 9. Every matrix entry is
linear in \(a,b,c\), and its vector after \(n\) rows is homogeneous of degree
\(n\). The coefficient of \(S^j\) in \(g(S)^4\) is homogeneous of degree
\(16-j\). Thus every coordinate of
\[
 \sum_{j=0}^{16}[S^j]g(S)^4\;T^jv_9                       \tag{4}
\]
is homogeneous of degree 25.

The exact verifier checks all coordinates of (4), for both parity blocks,
at every point
\[
 c=1,\qquad a,b\in\mathbb Z_{\ge0},\quad a+b\le25.
\]
There are 351 points and 702 complete vector identities. To see completeness,
let a polynomial of total degree at most 25 vanish on this triangle.
At \(b=0\), its restriction has 26 distinct roots in \(a\), so it is divisible
by \(b\). At \(b=1\), the quotient has 25 roots in \(a\), so it is divisible
by \(b-1\). Continue through \(b=25\); the original polynomial is zero.
Homogeneity then recovers the entire polynomial in \(a,b,c\), including
\(c=0\). This proves the vector identity universally.

For each block, the eight early scalar residues at \(n=1,\ldots,8\) have
degrees \(n+16\le24\). The same complete triangle verifies them, giving
5,616 early identities. Together with (4), they prove the lemma. This is a
finite polynomial-identity proof, not an inference from a scalar prefix.
The executable leaf is verify_sequence_quadratic_hankel.py and its pinned run.

For orientation, the stationary symbol has the exact factorization
\[
 z^4T(z)=(1-z)^4\{2a(1-z)^4+4bz(1-z)^2+24cz^2\}.             \tag{5}
\]
It follows by summing the two difference stencils against
\(\tau(2n)=2(b-c)|n|+2c|n|^3\) for \(n\ne0\), with \(\tau(0)=2a\).
This explains the repeated fixed roots. Identity (5) alone does not establish
the boundary-vector annihilator (4).

## 4. Uniform full-sequence order at most 126

Set
\[
 A=4a^2,\quad p=-8a+8b-24c,\quad
 q=24a^2-32ab-96ac+16b^2.
\]
Then \(g(X)=X^4+pX^3+qX^2+ApX+A^2\). Define the monic degree-nine polynomial
\[
 \begin{aligned}
 h(Y)={}&(Y-A)h_{\rm d}(Y)h_{\rm c}(Y),\\
 h_{\rm d}(Y)={}&(Y^2+qY+A^2)^2-p^2Y(Y+A)^2,\\
 h_{\rm c}(Y)={}&Y^4-(q-2A)Y^3\\
 &+\{A(p^2-2q)+2A^2\}Y^2-A^2(q-2A)Y+A^4.
 \end{aligned}                                               \tag{6}
\]

**Theorem H.** For every \(a,b,c\) in a characteristic-zero field,
\[
 \boxed{h(S^2)^7W_n=0\quad(n\ge2).}                         \tag{7}
\]
Its order is at most 126. The OGF denominator is
\(z^{126}h(z^{-2})^7\), which has constant term one; trailing zero
coefficients and cancellations can reduce its degree.

**Proof.** Regard \(A,p,q\) first as independent indeterminates. Monic
polynomial division, first in \(x\) and then in \(y\), gives the identity
\[
 h(xy)=U(A,p,q,x,y)g(x)+V(A,p,q,x,y)g(y)                    \tag{9}
\]
in \(\mathbb Z[A,p,q,x,y]\). The executable algebraic leaf
verify_sequence_hankel_symbol.py computes both quotient polynomials and checks every
coefficient of the reconstructed identity. Its saved result contains every
monomial of \(U,V\); no parameter sampling or root approximation is used.

Raise (9) to the seventh power. Every term of its binomial expansion
contains either \(g(x)^4\) or \(g(y)^4\). Therefore
\[
 h(xy)^7\in(g(x)^4,g(y)^4).
\]
For the companion \(C\) of \(g^4\), substitute \(x=C\otimes I\) and
\(y=I\otimes C\). The matrices commute and both fourth powers of their
\(g\)-values vanish. Thus \(h(C\otimes C)^7=0\). This argument applies
directly at every specialization, including \(a=0\), \(c=0\), colliding
roots, and the zero weight.

The lemma represents both block sequences by this companion from index one.
Apply the tensor identity to \(A_mB_m^{\rm o}\), and separately to
\(A_{m+1}B_m^{\rm o}\), then use (1). This gives (7) for both parities.
The exceptional value \(W_0\) is retained separately. \(\square\)

## 5. Exact minimal order 63 at the first nonlinear example

**Theorem I.** Let \(P(m)=1+m^2\) and \(\mathcal D=1\), equivalently
\((a,b,c)=(1,1,1)\). Put
\[
 \begin{aligned}
 \Gamma(X)={}&(X-2)(X^4-24X^3-88X^2-96X+16)\\
 &\qquad\cdot(X^4-4X^3+56X^2-16X+16).
 \end{aligned}
\]
Then
\[
 \boxed{\Gamma(S)^7W_n=0\quad(n\ge1),}
\]
and the minimal eventual order is exactly 63.

The rational OGF has reduced denominator
\[
 \{(1-2z)(1-24z-88z^2-96z^3+16z^4)
             (1-4z+56z^2-16z^3+16z^4)\}^{7}.                \tag{8}
\]
The numerator has degree 63. All 64 coefficients are retained in the exact
certificate JSON. Equivalently, it is the truncation through degree 63 of
(8) times the defining determinant series.

**Certificate proof.** The two 70-state block relations are checked exactly.
The discovery calculation then verifies complete identities on two
136-coordinate symmetric-product vectors. A separate implementation instead
uses ordinary 256-coordinate tensors, initializes them from 52 direct
monomial block determinants, and recomputes both complete identities.
Thus the unreduced degree-126 rational OGF follows for the infinite sequence.
Exact polynomial cross multiplication checks its equality to the reduced
numerator divided by (8).

The reduced numerator and denominator have preserved degrees modulo the
verified prime 1000003. The saved polynomials \(U,V\) satisfy
\(UN+VD=1\) in that finite field, with every coefficient checked. A common
nonconstant rational factor would retain positive degree on reduction at
this prime, since both leading coefficients survive; hence the rational
polynomials are coprime. The denominator degree is 63, which proves eventual
minimality. Its numerator degree also proves the stated recurrence start.

The first values are
\[
 1,\ 1,\ 4,\ 56,\ -1400,\ 234000,\ 92664000,\ 13067049600.
\]
Direct Hankel determinants through size 20 and 192 values from the separate
Schur solver agree. They are regression checks; the complete vector identities
and polynomial comparison are the infinite-sequence certificate.

## 6. Scope and continuation

The general parity proof includes all finite parity-definite operators and
all zero minors. The explicit quartic lemma and bound (7) apply uniformly to
quadratic weights with the identity operator. The exact order 63 is asserted
at the stated sample. A sharp universal degree-63 formula, and a uniform
minimal recurrence for genuinely mixed operators, remain separate obligations.

Finite evidence is in the parity-structure, uniform-quadratic,
quadratic-certificate and quadratic-audit runs. This is a self-reviewed
computer-assisted proof, not a Lean certificate or independent review.
