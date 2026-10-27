# First irregular lower address: one surviving critical scale

Date: 2026-10-05. This is a new theorem for the actual Euler finite prefix at lower address 17. It retains the certified true terminal and all remote multiplier carries. It does not infer analytic descent from a smaller representation of the same depth.

## Statement

Let \(j=k+17\) be a certified true terminal whose last lower minimizing address is 17, with regular complement \(k\). Assume

\[
v_2(k)=53,
\qquad r=B2^L-j>0,
\qquad L=\Theta(k)+\delta,\quad \delta\ge0.
\]

The odd positive multiplier \(B\) is unrestricted apart from the stated actual-terminal and wall hypotheses. Write \(k=2^{53}c\), with \(c\) odd.

For every such actual Euler depth, define the finite prefix

\[
S(x)=\sum_{q=0}^{16}c_{r,q}P_q(x)\mathscr A(x-q),
\qquad c_{r,q}=8^q\beta_{r+q}/\beta_r.
\]

Then \(S\) has exactly one dyadic root \(\sigma\), it is simple, and

\[
\boxed{\sigma\equiv43\pmod{64},\qquad v_2(\sigma-11)=5.}
\tag{1}
\]

Every dyadic root of \(G_r\) above an emerged complement ball is simple. Every root above a root-free complement ball satisfies

\[
v_2(x-11)=5,\qquad v_2(x-\sigma)=16.
\tag{2}
\]

Such a root can be multiple only if

\[
\delta=d_i+16,
\qquad
L=4k+16-v_2\binom{c-1}{b},
\tag{3}
\]

where its complement skeleton index has the form \(i=2^{53}b+\rho\), \(0\le b<c\), \(0\le\rho<2^{53}\).

In particular, for the first complement \(k=2^{53}\), **every certified wall at every outer scale is simple except possibly**

\[
\boxed{L=4\cdot2^{53}+16.}
\tag{4}
\]

At this scale the only possible multiple roots have the exact distance in (2). This is a necessary condition, not a claim of an existing tangency. Equality walls \(\delta=0\) are simple as well.

## 1. Exact normalization and prefix factorization

For the smaller label 17,

\[
\Theta(17)=L_{17}=53,
\quad
(e_{17}(q))_{q=0}^{16}
=(0,0,4,7,11,13,17,20,24,25,29,32,36,38,42,45,49).
\]

The first two packets compete, but every other prefix packet is even. Thus

\[
S\equiv1+X\pmod2
\]

coefficientwise. The degree-one preparation theorem gives the exact factorization

\[
S(x)=(x-\sigma)V(x),
\qquad V\in\mathbb Z_2\langle x\rangle^\times,
\quad V\equiv1\pmod2.
\tag{5}
\]

Here \(\sigma\) is the unique simple odd root. Since \(t=53=\Theta(17)\), the quantity called \(D=t-\Theta(a)\) in the regular-address theorem is zero. Actual tail splitting and true-terminal inheritance therefore give

\[
G_r(x)=uP_{17}(x)F(x-17)+2^\delta S(x),
\qquad F=G_{r+17},\quad u\in\mathbb Z_2^\times.
\]

Set \(q(x)=uP_{17}(x)/V(x)\). Multiplicity is unchanged on dividing by \(V\), and the exact equation becomes

\[
\boxed{G_r(x)/V(x)=q(x)F(x-17)+2^\delta(x-\sigma).}
\tag{6}
\]

This is the required replacement for division by a prefix that has a zero. It is analytic everywhere, including at \(x=\sigma\).

There is also an exact relation to the adjacent actual Euler depth. Define

\[
T(z)=\sum_{h=0}^{15}c_{r+1,h}P_h(z)\mathscr A(z-h).
\]

The packet cocycle gives

\[
S(x)=\mathscr A(x)+c_{r,1}P_1(x)T(x-1),
\tag{6a}
\]

and

\[
H_{r+1}(z)=T(z)+c_{r+1,16}P_{16}(z)H_{r+17}(z-16).
\tag{6b}
\]

Here \(T\equiv1\pmod2\), because address 16 is regular. The actual true terminal of \(r+1\) is \(k+16\), not 16. Its last lower address is 16 and its complement valuation is 53. Since \(\Theta(16)=53\) and \(v_2(16!)=15\), the regular-address theorem already proves simplicity of every root of this adjacent Euler function at every wall distance. Equations (6a)–(6b) explicitly retain its remote regular complement. They give an exact analytic route through the neighboring regular address, while the possible tangency of the added address-one transition remains the obligation isolated below.

## 2. A uniform six-bit certificate for the actual prefix

The actual depth satisfies \(r\equiv-17\pmod{2^{53}}\), because both \(k\) and \(B2^L\) are divisible by \(2^{53}\). For the finite prefix this congruence is sufficient. It does not assert that the true terminal has become 17.

The Bernoulli distribution identity yields, for each actual positive even index \(n\) involved,

\[
2B_n\equiv\sum_{h=0}^{6}\binom nh2^hB_h\pmod{64}.
\tag{7}
\]

The undepletion denominator \(1-2^{n-1}\) is 1 modulo 64, since these actual indices are much larger than 7. Terms beyond 6 vanish modulo 64. Substitution of the congruent negative integer \(-34+2q\) in the finite polynomial on the right is legitimate: the difference of the falling products in \(\binom nh\) is divisible by \(2^{54}\), and division by \(h!\) loses at most \(v_2(h!)\le h-1\) bits. The factor \(2^hB_h\) has valuation at least \(h-1\). Thus each term keeps far more than six valid bits. This is a polynomial congruence calculation, not a claim about Bernoulli numbers of negative index.

It gives

\[
2B_{2r}\equiv13,\quad 2B_{2r+2}\equiv1,\quad
2B_{2r+4}\equiv21\pmod{64}.
\]

For \(q\le2\), the factorial factors \(2r+h\) have the same valuations as \(-34+h\); the largest is 5. Removing those powers loses at most five of the 54 available congruence bits. Therefore the exact stripped coefficient formula gives

\[
c_{r,0}\equiv1,\qquad c_{r,1}\equiv55,\qquad c_{r,2}\equiv16\pmod{64}.
\tag{8}
\]

For instance \(c_{r,1}\equiv(35\cdot13)^{-1}\equiv55\pmod{64}\). Every \(q\ge3\) prefix coefficient has valuation at least 7, so none contributes modulo 64.

The source expansion with \(\log9/8\equiv61\pmod{64}\) gives

\[
\mathscr A(x)\equiv1+34x+28x^2+8x^3+48x^4+32x^5\pmod{64}.
\]

Substituting this and (8) into the three remaining packets gives the coefficientwise identity

\[
\boxed{S(x)\equiv1+13x+40x^2+8x^3+48x^4+32x^5\pmod{64}.}
\tag{9}
\]

Its unique root modulo 64 is 43, proving (1). The accompanying standard-library checker reconstructs (8) and (9), independently checks the Bernoulli residues against exact small positive Bernoulli numbers, and checks the source coefficients against the rational source at 64 integer arguments. The proof of transfer to all actual \(B,L\) is the explicit congruence and loss argument above.

## 3. Geometry of the prefix root

Use the lower skeleton partition for \(P_{17}\). On its ball centered at \(\ell\in\{0,\ldots,16\}\), let

\[
g_\ell=v_2(\ell!)+v_2((16-\ell)!),\quad
h_\ell=1+\lfloor\log_2\max(\ell,16-\ell)\rfloor.
\]

All \(h_\ell\le5\), all \(g_\ell\ge11\), and the ball containing \(\sigma\) is precisely \(11+16\mathbb Z_2\), where \(g_{11}=11\) and \(h_{11}=4\).

For \(x\ne\ell\) on the ball centered at \(\ell\), put

\[
s=v_2(x-\ell),\qquad w=v_2(x-\sigma).
\]

Because division by \(V\) preserves the skeleton's coefficientwise affine reduction,

\[
v_2q(x)=g_\ell+s,\qquad v_2q'(x)=g_\ell.
\tag{10}
\]

Outside the lower ball centered at 11, \(w=v_2(\ell-\sigma)<h_\ell\le5\). Inside it, (1) gives the exhaustive cases

\[
\begin{array}{c|c}
s & w\\\hline
4&4\\
5&\ge6\\
>5&5.
\end{array}
\tag{11}
\]

At a root over a root-free complement ball, \(v_2F=\delta\). Equation (6) therefore requires \(g_\ell+s=w\). Outside the special ball, the right side is smaller than \(h_\ell\), while the left side is at least \(g_\ell+h_\ell\). Inside it, the only possibility in (11) is \(s=5\), \(w=11+5=16\). This proves (2).

## 4. Every emerged complement branch is simple

For a complement skeleton ball \(B_i\), put

\[
d_i=v_2(i!)+v_2((k-1-i)!),\qquad
H_i=1+\lfloor\log_2\max(i,k-1-i)\rfloor\ge53.
\]

Suppose the ball has emerged, so \(\delta\ge d_i+H_i\). Write its unique simple root as \(\alpha_i\), set \(\gamma=\alpha_i+17\), and let

\[
z=v_2(x-\gamma)\ge H_i.
\]

The regular atlas gives \(v_2F=d_i+z\), \(v_2F'=d_i\), and \(v_2(\gamma-(i+17))=\delta-d_i\).

First suppose \(x\ne\sigma\). Equation (6) forces \(q(x)F(x-17)\ne0\), so all valuations used below are finite. At a multiple root, eliminating the constant \(2^\delta\) between (6) and its derivative gives

\[
[(x-\sigma)q'-q]F+(x-\sigma)qF'=0.
\]

Consequently

\[
z=w+g_\ell+s-v_2((x-\sigma)q'-q)
\le\max(s,w).
\tag{12}
\]

The last inequality follows because the subtracted terms have valuations \(w+g_\ell\) and \(g_\ell+s\). If their difference is zero, the other displayed summand is nonzero and tangency is already impossible.

Since \(z\ge H_i\ge53\), at least one of \(s,w\) is at least \(H_i\). They cannot both be, because \(v_2(\sigma-\ell)\le5\).

If \(w\ge H_i\), then \(\ell=11\), \(s=5\), and the two terms in the difference have unequal valuations. Its valuation is 16, and (12) is the equality \(z=w\). The root equation (6) now gives

\[
\delta-d_i=g_\ell+s+z-w=16,
\]

contrary to emergence, which requires \(\delta-d_i\ge H_i\ge53\).

If \(s\ge H_i\), then \(w=v_2(\sigma-\ell)\le5\). The difference has valuation \(g_\ell+w\), so \(z=s\), and the root equation gives

\[
\delta-d_i=2s+g_\ell-w>H_i.
\]

The translated complement ball contains the integer \(\ell\). As in the regular-address proof,

\[
0<i+17-\ell<2^{H_i+1},\qquad
2^{H_i}\mid i+17-\ell,
\]

so \(i+17-\ell=2^{H_i}\). Since \(\gamma\) is farther than \(H_i\) bits from that center, \(v_2(\gamma-\ell)=H_i\). Dyadic parity then makes \(v_2(x-\gamma)=s\) impossible: if \(s>H_i\), its value is \(H_i\); if \(s=H_i\), its value is strictly larger. This contradiction closes this case.

Finally let \(x=\sigma\). Equation (6) can vanish only if \(F(\sigma-17)=0\), since \(q(\sigma)\ne0\). At this simultaneous zero, (1) and (10) give \(v_2q(\sigma)=16\), so

\[
v_2(q(\sigma)F'(\sigma-17))=16+d_i<\delta.
\]

This term is the unique least-valuation term in the derivative of (6). Hence the simultaneous zero is simple as well. No division by a vanishing prefix was used.

## 5. Root-free branches and the one-scale obstruction

By (2), every root-free root has \(v_2q=16\), \(v_2q'=11\), and \(v_2F=\delta\). The three derivative terms in (6) have valuations

\[
\delta+11,\qquad 16+v_2F',\qquad\delta.
\]

If \(d_i>\delta\), then \(v_2F'>\delta\), so the last term dominates. If \(d_i\le\delta\), the complement's skeleton derivative dominates its even analytic correction, and \(v_2F'=d_i\). The derivative can therefore vanish only if

\[
\delta=d_i+16.
\]

For \(i=2^{53}b+\rho\), the factorial digit-sum identity gives

\[
d_i=k-54-s_2(b)-s_2(c-1-b).
\]

Since \(\Theta(k)=3k+54+s_2(c-1)\), adding gives (3). For \(c=1\), \(d_i=k-54\) on every complement ball, so the only surviving distance is \(\delta=k-38\) and the only surviving outer scale is (4).

At \(\delta=0\), the regular complement is unit-valued with even derivative. The same root valuation argument still gives (2). In the derivative of (6), the first term has valuation 11, the second has valuation at least 17, and the constant derivative has valuation 0. Thus all equality-wall roots are simple.

## Exact remaining obligation

For the first irregular lower-address family, at its sole critical outer scale, every possible multiple root has \(v_2(x-\sigma)=16\). At such a root the prefix derivative and complement derivative terms have equal valuation, while the other term is eleven bits higher. Their actual odd units could still cancel. This note isolates that exact arithmetic obligation and does not claim to resolve it.

This is a valid analytic reduction for an irregular lower address, obtained by preparing its finite prefix into a linear root factor. The original remote carries remain in \(F=G_{r+17}\), its degree \(k\), and its actual Euler coefficients. No new Lean compilation is claimed.
