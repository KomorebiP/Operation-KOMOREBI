# A certified mixed weight/operator recurrence

Author: Komorebi P. Checkpoint: SEQ-DH-2026-11-20-002.

## Exact claim

Use the determinant convention of PARITY_HANKEL_RECURRENCES.md, with
\[
 P(m)=1+m,\qquad \mathcal D=1+2\partial_x.
\]
The defining moments are explicitly
\[
 \mu_{2m}=(m+1)\binom{2m}{m},\qquad
 \mu_{2m+1}=2(2m+1)(m+1)\binom{2m}{m}.
\]
The initial determinant values include
\[
 W_0=1,\quad W_1=1,\quad W_2=0,\quad W_3=-256,\quad
 W_4=44536,\quad W_5=3886128.
\]
The zero second minor is part of the claim.

Define
\[
 \begin{aligned}
 B(z)={}&1-16z+384z^2+1600z^3-21568z^4+129792z^5\\
 &+649216z^6-2378752z^7+9340416z^8-9515008z^9\\
 &+10387456z^{10}+8306688z^{11}-5521408z^{12}\\
 &+1638400z^{13}+1572864z^{14}-262144z^{15}+65536z^{16}.
 \end{aligned}
\]
Put \(b(X)=X^{16}B(X^{-1})\).

**Theorem J.** The determinant sequence satisfies
\[
 \boxed{b(S)^7W_n=0\quad(n\ge1).}
\]
Its rational OGF has reduced denominator \(B(z)^7\), and its minimal
eventual recurrence order is exactly 112. The numerator has degree 112;
all 113 coefficients are retained in the certificate. It is also defined
without a fitted recurrence as the truncation through degree 112 of
\(B(z)^7\sum_{N\ge0}W_Nz^N\), using the explicit moment determinants.

## Infinite-sequence proof

The inherited boundary-safe banding gives half-bandwidth eight, stationary
row 17, and 12,870 signed matching states. Let \(T\) be the stationary
integer transfer and \(v_{17}\) its exact boundary vector. The decisive leaf is
the complete integer identity
\[
 b(T)^7v_{17}=0.
\]
Every coordinate is checked, with no modular reduction at this step. Applying
further powers of \(T\) proves the recurrence for every \(n\ge17\), not just
for computed determinants. Direct exact checks of the sixteen earlier scalar
residues extend the start to \(n=1\). The residue at \(n=0\) is nonzero.

The full-state identity first arose from a changed computation: sparse modular
propagation, projected recurrence discovery, and CRT reconstruction. Seven
verified primes give a 210-bit modulus, while the reconstructed coefficients
have maximum height 172 bits. Stabilization is a discovery criterion only.
The integer residual above, rather than CRT agreement, establishes the claim.

A separate standard-library implementation reconstructs the band matrix from
the displayed monomial moments and explicit Chebyshev polynomials. It uses
bitmask occupancy states instead of tuples. It recomputes the boundary vector,
stationary transfer, all 12,870 integer residual coordinates, and the GF
numerator. It imports neither the discovery transfer nor NumPy or SymPy.
The two implementations agree. This is separate-algorithm self-review, not
independent review.

## Minimality and validation

Exact multiplication reconstructs the denominator as \(B(z)^7\). The saved
finite-field Bezout coefficients verify \(UN+VD=1\) modulo the checked prime
1000003, and both numerator and denominator retain their degrees. Thus the
rational OGF is reduced. Its degree-112 denominator proves that no eventual
constant-coefficient scalar recurrence of smaller order exists.

Independent Schur calculations agree at 154 determinant sizes. Direct
fraction-free determinants through size 20, including the zero second minor,
agree as well. Adding one to the proposed recurrence's constant coefficient
has residual exactly \(v_{17}\ne0\), so the corrupted certificate is rejected.

The earlier 60-second dense rational elimination timeout is preserved. It was
a limitation of that extraction method; the new result does not erase that
record or turn its timeout into earlier evidence.

## Scope

This theorem is for the specified mixed example. It does not establish a
uniform order-112 recurrence for every linear weight and first-order operator,
or a general minimal-order law. Historical novelty and independent review
remain unassessed. Exact commands, inputs, software versions, outputs and
hashes are retained by the mixed-CRT and mixed-audit run manifests.
