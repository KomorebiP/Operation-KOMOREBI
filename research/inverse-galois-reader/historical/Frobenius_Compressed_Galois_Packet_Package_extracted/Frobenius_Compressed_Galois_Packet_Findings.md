# Frobenius-Compressed Galois Packet Multiplication

## 1. Motivation

The divided-square/refinement investigation closes strict nonlinear state contraction for the map
\[
Q(A)=\sum_{i<j}a_i a_j X^{i+j}
\]
in broad recursive packet classes.  A different route survives: retain a linear-size state, but choose a nonlinear multiplicative packet chart in which the mixed product disappears between packets.

## 2. Finite-field orbit packets

Let \(q=2^m\).  Over \(\mathbf F_2\),
\[
X^q-X=\prod_{P\in\mathcal I_m} P(X),
\]
where \(\mathcal I_m\) is the set of monic irreducibles whose degrees divide \(m\), each occurring once.  Hence
\[
\mathbf F_2[X]/(X^q-X)
\cong
\prod_{P\in\mathcal I_m}\mathbf F_{2^{\deg P}}.
\]
The dimensions satisfy
\[
\sum_{P\in\mathcal I_m}\deg P=q.
\]
Therefore the complete CRT packet state contains exactly \(q\) bits, not \(qm\) bits.

Equivalently, the \(q\) roots form Frobenius orbits.  If \(\alpha\) has orbit length \(d\), then for a binary polynomial \(A\),
\[
A(\alpha^{2^j})=A(\alpha)^{2^j}.
\]
One \(d\)-bit seed determines the \(d\) values on that orbit. Summing orbit lengths again gives \(q\).

If \(q>2n-2\), then for \(\deg A,\deg B<n\), the product has degree less than \(q\), so multiplication in this CRT product ring is the exact ordinary carryless product.

## 3. Nonlinear multiplicative packet chart

For every field packet \(K_P=\mathbf F_{2^d}\), choose a primitive generator \(g_P\). Encode zero by a distinguished code and every nonzero element \(g_P^e\) by its exponent. This is a bijection using exactly \(d\) bits because the field has \(2^d\) states.

In these packet coordinates multiplication is
\[
(0)\odot z=0,
\qquad
(e_1+1)\odot(e_2+1)
=
\bigl((e_1+e_2)\bmod(2^d-1)\bigr)+1.
\]
Thus the nonlinear multiplication core is exponent addition, with total coordinate width
\[
\sum_P d=q.
\]
The exact laboratory verified this complete analysis--packet-multiply--synthesis chain for \(q=2,4,8,16,32,64\).

## 4. Carry-bearing lift to powers of two

Let
\[
R_s=\mathbf Z/2^s\mathbf Z,
\qquad q=2^m.
\]
The polynomial \(X^q-X\) has derivative
\[
qX^{q-1}-1\equiv1\pmod2,
\]
so its residue roots lift uniquely to the Teichmuller set in the unramified Galois ring
\[
S=\operatorname{GR}(2^s,m).
\]
Distinct Teichmuller points remain separated by units, so the Vandermonde evaluation map is invertible.

The CRT form is
\[
R_s[X]/(X^q-X)
\cong
\prod_{P\in\mathcal I_m}\operatorname{GR}(2^s,\deg P),
\]
and the total base-ring rank is again
\[
\sum_P\deg P=q.
\]
Hence the exact packet state has
\[
\boxed{s q\text{ bits}}
\]
rather than the naive \(s q m\) bits obtained by materializing every extension-field evaluation.

For a base-ring polynomial \(A\), Frobenius equivariance gives
\[
A(\tau^{2^j})=\sigma^j(A(\tau)),
\]
so one seed per point orbit determines the whole orbit at every \(2\)-adic precision.

The laboratory explicitly constructed small Galois rings, Teichmuller lifts, Frobenius maps, Vandermonde interpolation, and verified the orbit identity through degrees \(m=2,3,4\) and precisions through \(2^4\).

## 5. Exact ordinary integer multiplication in one packet product

Let the two nonnegative \(n\)-bit integers be chunked in base
\[
B=2^b:
\qquad
a=\sum_{i=0}^{N-1}a_iB^i,
\quad
b'=\sum_{i=0}^{N-1}b_iB^i.
\]
Define coefficient polynomials
\[
A(Z)=\sum_i a_iZ^i,
\qquad
B(Z)=\sum_i b_iZ^i.
\]
Each exact convolution coefficient obeys
\[
0\le C_k< N(2^b-1)^2.
\]
Choose
\[
s=2b+\lceil\log_2N\rceil+1
\]
and choose \(q=2^m>2N-2\).  Then neither coefficient reduction modulo \(2^s\) nor degree reduction modulo \(Z^q-Z\) changes the product. Therefore:

1. evaluate \(A,B\) in the Frobenius-compressed Galois packets;
2. multiply corresponding packets;
3. synthesize the exact coefficients \(C_k\);
4. perform the ordinary base-\(2^b\) carry pass.

This recovers the exact integer product.

The laboratory verified the construction for \(N=2,3,4\), chunk widths \(b=1,2,3\), and randomized operands. Every tested product matched Python's exact integer multiplication.

## 6. Linear state bound

Take
\[
b=\lceil\log_2 n\rceil,
\qquad
N=\lceil n/b\rceil.
\]
Then
\[
q<4N,
\qquad
s=O(\log n),
\]
so
\[
\boxed{s q=O(n).}
\]
More explicitly, asymptotically the packet state is at most a constant multiple of the \(2n\)-bit output size. Thus the earlier \(\Omega(\log n)\) extension degree is not itself a state-size obstruction once Frobenius orbits are compressed.

## 7. What is and is not solved

This is an exact, one-shot, carry-bearing multiplication architecture with:

- linear total packet dimension;
- no cross interaction between distinct CRT packets;
- exact recovery of ordinary integer products;
- a natural multiplicative-coordinate chart in each packet where the multiplication core becomes coordinate addition.

It is **not yet an O(n)-bit-operation multiplier**.  The unresolved operation is the global forward/inverse transform
\[
\Lambda_{m,s}:
R_s[X]_{<q}
\longleftrightarrow
\prod_{P\in\mathcal I_m}
\text{multiplicative coordinates of }\operatorname{GR}(2^s,\deg P).
\]
The strict-contraction no-go results do not eliminate this route because \(\Lambda_{m,s}\) is dimension preserving, globally nonlocal, stratified at zero, and nonlinear after the multiplicative coordinate step.

The remaining breakthrough target is therefore sharper than before:

\[
\boxed{
\text{Construct the forward and inverse Frobenius-compressed Galois packet transforms in }O(sq)\text{ bit work.}
}
\]

With \(b\asymp\log n\), \(sq=O(n)\).  If these transforms can be realized with linear work, the packet multiplication and final carry normalization are also linear-width operations, yielding a plausible route to \(O(n)\) exact integer multiplication.

## 8. Important correction to the earlier extension-degree objection

The statement that an unramified extension of degree \(m=\Omega(\log n)\) necessarily creates an \(n\log n\)-sized state is too pessimistic if it assumes all conjugate evaluations are materialized independently. Frobenius compression removes that factor at the representation level:
\[
q\times m\text{ naive extension symbols}
\quad\rightsquigarrow\quad
\sum_{\text{orbits}}\text{orbit degree}=q.
\]
The logarithmic extension degree may still reappear in transform **time**, but it is not forced in transform **state size**.
