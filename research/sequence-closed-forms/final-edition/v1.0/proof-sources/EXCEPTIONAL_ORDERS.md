# Minimal recurrence orders on the mixed-family coordinate boundary

Author: Komorebi P. Checkpoint: SEQ-DH-2026-11-21-004.
Parent publication: 15a218cb60f08a4830573f17bca2bbfd2585bf9c.
Review status: proved as written in separate project self-review;
no independent review or Lean formalization.

## 1. Statement and complete boundary table

Over a characteristic-zero field, use
\[
 \begin{aligned}
 \mu_{2m}&=u(a+bm)\binom{2m}{m},\\
 \mu_{2m+1}&=v(2m+1)(a+bm)\binom{2m}{m},\\
 W_N&=\det(\mu_{i+j})_{0\le i,j<N},\qquad W_0=1.
 \end{aligned}
\]
The minimal order below always means the minimal **eventual scalar
constant-coefficient recurrence order**. Order zero means eventual vanishing.
The uniform bound 112 and generic minimality are established in the
[preceding mixed-family theorem](UNIFORM_MIXED_RECURRENCE.md).

**Theorem M.** Suppose \(abuv=0\). If \((a,b)=(0,0)\) or
\((u,v)=(0,0)\), the minimal order is zero. Otherwise the following table
is exhaustive. Its families are read in order, so intersections are included.

| Family | Further condition | Minimal order |
|---|---|---|
| \(v=0,\ u\ne0\) | \(a=0\) | 3 |
| \(v=0,\ u\ne0\) | \(a\ne0,\ b=0\) | 1 |
| \(v=0,\ u\ne0\) | \(a\ne0,\ b=2a\) | 7 |
| \(v=0,\ u\ne0\) | \(a\ne0,\ b\notin\{0,2a\}\) | 9 |
| \(u=0,\ v\ne0\) | \(a=0\) | 14 |
| \(u=0,\ v\ne0\) | \(a\ne0,\ b=0\) | 6 |
| \(u=0,\ v\ne0\) | \(a\ne0,\ b=a/3\) | 26 |
| \(u=0,\ v\ne0\) | \(a\ne0,\ b=2a/3\) | 18 |
| \(u=0,\ v\ne0\) | \(a\ne0,\ b\notin\{0,a/3,2a/3\}\) | 42 |
| \(b=0,\ auv\ne0\) | \(v^2+16u^2=0\) | 10 |
| \(b=0,\ auv\ne0\) | \(v^2+16u^2\ne0\) | 12 |
| \(a=0,\ buv\ne0\) | \(9v^2+16u^2=0\) | 22 |
| \(a=0,\ buv\ne0\) | \(9v^2+16u^2\ne0\) | 28 |

The reduced recurrence in every row holds from index one. The zero-index
empty determinant is retained separately. The two quadratic-relation rows
with orders 10 and 22 have no nonzero real solutions for \(u,v\); they
matter over fields containing the required square roots of -1.

This theorem classifies the entire coordinate boundary. It does not classify
the fully nonzero locus \(abuv\ne0\).

## 2. Smaller uniform recurrences from formal moment functionals

Put \(\sigma=x^2-4\), and define formal residues at infinity by
\[
 \begin{aligned}
 \rho_1[f]&=[x^{-1}]f(x)\sigma^{-3/2},\\
 \rho_2[f]&=[x^{-1}]f(x)\sigma^{-5/2}.
 \end{aligned}
\]
The second functional is the \(\nu\) of the preceding proofs, and
\(\rho_1=\sigma\rho_2\). Their even moments are respectively
\(m\binom{2m}{m}/2\) and \(m(m-1)\binom{2m}{m}/12\); odd moments vanish.

For \(n\ge3\), the monic formal orthogonal polynomials for \(\rho_1\) are
\[
 q_n=\frac{\sigma^{3/2}}{(2n-3)!/(n-3)!}
                   \partial_x^n\sigma^{n-3/2}.
\]
The Rodrigues expression is monic, and formal integration by parts gives
orthogonality. More explicitly, its norm is
\[
 \begin{aligned}
 \rho_1[q_n^2]&=\rho_1[q_nx^n]\\
 &=\frac{(-1)^n n!}{(2n-3)!/(n-3)!}\\
 &\quad{}\cdot(-4)^{n-1}\binom{n-3/2}{n-1}\\
 &=-\frac{2n}{n-2}\ne0.
 \end{aligned}
\]
The size-three base Gram determinant is -1.
Consequently
\[
 H_N(\rho_1)=\frac{(-2)^N(N-1)(N-2)}{16}\quad(N\ge3).
\]
The operator \(\sigma\partial_x^2-x\partial_x\) is formally self-adjoint
because \((\sigma\sigma^{-3/2})'=-x\sigma^{-3/2}\). Orthogonality and
nonsingularity give \(\sigma q_n''-xq_n'=n(n-2)q_n\). Its monic solution
is unique, since the eigenvalue difference at degree \(j<n\) is
\((n-j)(n+j-2)\ne0\). With \(x=z+z^{-1}\), substitution therefore gives
\[
 (n-2)q_n(x)=(n-2)C_n(x)-nC_{n-2}(x),
 \qquad C_n(z+z^{-1})=z^n+z^{-n}.
\]
The coefficients of the two exponential branches have degree one in \(n\).
These assertions also have separate exact polynomial, orthogonality and norm
checks in the replay. The Rodrigues/orthogonality argument is the same formal
residue argument as in [Theorem K](SHARP_QUADRATIC.md), with the displayed
exponent changed; it uses no positive measure.

For a quadratic \(R=A x^2+B x+C\) multiplying \(\rho_1\), the two-root
augmented-Vandermonde identity therefore has four bases and coefficient
degree at most two. Their base polynomial is
\[
 X^4+2CX^3+(4B^2-8AC-8A^2)X^2+8A^2CX+16A^4.
\]
Indeed, if the two roots are \(r=z+z^{-1}\), \(s=w+w^{-1}\), the bases
are \(-2Az^{\pm1}w^{\pm1}\). Their elementary symmetric functions use
\(r+s=-B/A\) and \(rs=C/A\), giving the displayed polynomial.
Its cube is a uniform order-12 annihilator. The normalization of the raw
two-root determinant is \((-2A)^N/16\). Its initial indices one and two
agree with the actual determinants by coefficient identities; its value
at zero is 1/2. For even \(R\), the four branches give three distinct bases
generically, so the bound improves to nine. The resulting characteristic
factor for \(u=1\) is the previously published
\((X-2a)(X^2-4(a-b)X+4a^2)\); scaling the functional by \(u\) scales
every exponential base by \(u\).

For a quadratic multiplying \(\rho_2\), use the raw polynomials
\(P_n=(n-3)(n-4)p_n\) from Theorem K. The normalization is
\[
 \frac{(2A)^N(N-1)(N-2)}{4608}.
\]
The determinant of two raw branches has coefficient degree at most four;
the extra factor has degree two. Thus four bases give the uniform bound 28,
with seventh powers of
\[
 X^4-2CX^3+(4B^2-8AC-8A^2)X^2-8A^2CX+16A^4.
\]
Indices one through four are exact coefficient identities, using the same
low raw polynomials as Theorem L; the zero-index continuation is 1/8.

Finally, for the odd cubic \(R=d x(x^2-r^2)\) multiplying \(\rho_2\), the
three-root determinant has normalization \((-2d)^N/4608\). Every odd-size
determinant vanishes. The roots \(0,r,-r\), with \(r=z+z^{-1}\), give the
six possible full-sequence bases
\[
 \{\pm2id,\ \pm2id z^2,\ \pm2id z^{-2}\}.
\]
Each coefficient has degree at most six, so their seventh powers give a
uniform order-42 recurrence. Here \(i^2=-1\) is used in an algebraic extension
only; the resulting characteristic polynomial has coefficients in the
original field. For \(d=av\), \(r^2=4-6b/a\), it is
\[
 \left[(X^2+4a^2v^2)
 \{X^4+(8a^2-96ab+144b^2)v^2X^2+16a^4v^4\}\right]^7.
\]
For the initial boundary, divide the raw polynomials by the monic cubic
\(x^3-r^2x\) and take the three-by-three remainder coefficient determinant.
The identities at indices one through four agree coefficientwise with the
actual moment determinants. At zero the continuation is 1/4.

For all three constructions, the generic calculation takes place where the
displayed root determinants are nonsingular. For each fixed recurrence index,
the residue is a polynomial in the original coefficients. Thus the identities
extend to all specializations, including repeated roots and degree drops.
No inverse singular minor or limiting inference from numeric roots is used.

## 3. Four normalized generating-function certificates

The boundary functionals reduce exactly as follows:
\[
\begin{aligned}
 b=0:&\quad L=a[u\sigma+vx]\rho_1,\\
 a=0:&\quad L=2b[u\sigma+3vx]\rho_2,\\
 u=0:&\quad L=vx[a\sigma+6b]\rho_2,\\
 v=0:&\quad L=u[a\sigma+2b]\rho_1.
\end{aligned}
\]
The first identity uses the central-binomial functional
\(F_1[f]=[x^{-1}]f\sigma^{-1/2}=\rho_1[\sigma f]\) and formal integration
by parts; the others follow either the same way or from Theorem L's explicit
quartic functional. Hence the smaller recurrence bounds above apply.

Use the following normalized variables. In each row the generating function
is \(N_t(s)/Q_t(s)^e\), with \(Q_t(0)=1\).

| Family | Normalization | \(Q_t(s)\) | \(e\) | Degree bound for \(N_t\) |
|---|---|---|---|---|
| \(v=0,\ au\ne0\) | \(t=b/a,\ s=auz\) | \((1-2s)(1-4(1-t)s+4s^2)\) | 3 | 9 |
| \(b=0,\ au\ne0\) | \(t=(v/u)^2,\ s=auz\) | \(1-8s+(24+4t)s^2-32s^3+16s^4\) | 3 | 12 |
| \(a=0,\ bu\ne0\) | \(t=9(v/u)^2,\ s=2buz\) | \(1+8s+(24+4t)s^2+32s^3+16s^4\) | 7 | 28 |
| \(u=0,\ av\ne0\) | \(t=b/a,\ s=(avz)^2\) | \((1+4s)(1+(8-96t+144t^2)s+16s^2)\) | 7 | 21 |

The last row is the generating function of the even subsequence, since every
odd term is zero. Its denominator degree in \(s\) must be doubled to obtain
the full-sequence recurrence order in \(z\).

The exact numerator coefficient lists are retained in the certificate JSON.
They are defined without fitting an infinite recurrence: convolve the stated
denominator with the defining moment determinants, through the listed degree.
The smaller recurrence proves that later coefficients vanish.

These numerator coefficients are polynomials in \(t\). Their degree bounds at
coefficient index \(j\) are, respectively, \(j,\lfloor j/2\rfloor,
\lfloor j/2\rfloor,2j\). Homogeneity of a determinant in its functional
coefficients gives these bounds. In the two squared-ratio rows, reversing the
sign of the odd coefficient is the basis change \(x\mapsto-x\), so only its
even powers remain. The 10, 7, 15 and 43 distinct interpolation nodes in the
certificate therefore determine every coefficient. The replay evaluates all
coefficients at exactly those nodes and checks the stated bounds.

## 4. Minimality for every parameter in each normalized family

For each row, the certificate supplies polynomials \(U_t,V_t\) such that
\[
 U_t(s)N_t(s)+V_t(s)Q_t(s)=H(t).
\]
All coefficients of these identities are checked over \(\mathbb Q[t,s]\).
The right sides are exactly
\[
\begin{aligned}
 H_{v=0}(t)&=8t^5(t-2),\\
 H_{b=0}(t)&=2t^3(t+16),\\
 H_{a=0}(t)&=80t^7(t+16)^3,\\
 H_{u=0}(t)&=79254226206720\,t^{10}(3t-2)^7(3t-1)^7.
\end{aligned}
\]
Thus outside the listed roots of \(H\), the numerator is coprime to
\(Q\), hence to \(Q^e\). Its reduced denominator has full degree.
No other exceptional parameter in that normalized family is possible.

At the roots of \(H\), exact cross multiplication checks the following
reduced denominators. Separate rational Bezout identities certify that each
reduced numerator is coprime to its displayed denominator.

| Family | \(t\) | Reduced denominator in \(s\) | Degree |
|---|---|---|---|
| \(v=0\) | 0 | \(1-2s\) | 1 |
| \(v=0\) | 2 | \((1-2s)^3(1+2s)^4\) | 7 |
| \(b=0\) | 0 | \(1-2s\) | 1 |
| \(b=0\) | -16 | \((1+2s)^4(1-12s+4s^2)^3\) | 10 |
| \(a=0\) | 0 | \((1+2s)^3\) | 3 |
| \(a=0\) | -16 | \((1-2s)^8(1+12s+4s^2)^7\) | 22 |
| \(u=0\) | 0 | \((1+4s)^3\) | 3 |
| \(u=0\) | 1/3 | \((1+4s)^7(1-4s)^6\) | 13 |
| \(u=0\) | 2/3 | \((1+4s)^9\) | 9 |

Replacing \(s\) by a nonzero multiple of \(z\) preserves coprimality and
degree. Replacing it by \((avz)^2\) preserves coprimality by substituting
into the Bezout identity and doubles the denominator degree. A reduced
rational generating function's denominator degree is the minimal eventual
constant-coefficient recurrence order. This proves all normalized rows.

## 5. Remaining intersections and the empty determinant

The normalizations above omit two nonzero boundary intersections. Their
closed expressions, for \(N\ge1\), are
\[
 \begin{aligned}
 a=v=0:&\quad W_N=\frac{(-4bu)^N(N-1)(N-2)}{16},\\
 a=u=0:&\quad W_N=\frac{(N-1)^2(N-2)^2(N-3)^2}{1152}
          \{(12ibv)^N+(-12ibv)^N\}.
 \end{aligned}
\]
The first is the \(\rho_1\) base determinant scaled by \(2bu\); the second
is the one-root transform \(6bv x\rho_2\), using the same orthogonal
polynomials at zero. In detail,
\(H_N(cx\rho)=(-c)^NH_N(\rho)p_N(0)\), and for even \(N\ge6\)
the raw formula gives \(p_N(0)=8(-1)^{N/2}(N-1)/(N-4)\).
Odd indices vanish by parity. Their distinct nonzero exponential modes and nonzero
leading polynomial coefficients give minimal orders 3 and 14. Indices one
through four check the singular initial boundaries directly.

If \(b=u=0\), the corresponding expression is
\[
 W_N=\frac{(N-1)^2}{8}
                \{(2iav)^N+(-2iav)^N\}\quad(N\ge1),
\]
with minimal order six when \(av\ne0\). This follows from the same one-root
identity for \(avx\rho_1\), with
\(q_N(0)=4(-1)^{N/2}(N-1)/(N-2)\) at even \(N\ge4\).
If \(b=v=0\), it is
\(W_N=(2au)^N/2\) for \(N\ge1\), with minimal order one when \(au\ne0\).
These also agree with the appropriate normalized-family reductions.

Each nonzero family's reduced numerator has the same degree as its reduced
denominator; their leading coefficient ratio is nonzero. Consequently the
reduced recurrence starts at one and cannot include index zero. The
exponential continuations at zero are 1/2, 1/4, 1/8 or 1/16, depending on the
stratum, whereas the actual empty determinant is always one. Zero functionals
give \(W_N=0\) for \(N\ge1\), also with the start at one.

This completes the coordinate-boundary classification using the written
derivations and the replayed coefficientwise certificate leaves. Those leaves are finite
polynomial identities with proved coverage bounds, not sampled evidence for
an infinite pattern. Review remains project self-review; historical novelty,
independent review and Lean formalization are unassessed.
