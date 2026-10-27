# A matrix-capacity obstruction and explicit five-phase Fermat cycles

Komorebi research continuation, version 0.2.0. Session: 21 September 2026, America/Chicago.

## Status and scope

This note contains manuscript proofs and replayable exact algebraic certificates. It does not prove the general Hodge conjecture. It is not Lean-verified or independently reviewed.

The positive algebraicity family reconstructed here is the **known five-phase standard family of Aoki**. The family identification is recorded in Proposition 1.9 and the subsequent discussion of R. Jumagulov, arXiv:2608.18134v1, with reference to N. Aoki's 1987 paper. The original Aoki article was not successfully retrieved in this session. Accordingly, this note does not claim a new algebraicity theorem, priority for the defining equations, or priority for the determinant formula. The construction and calculation below are derived directly and use the independently checked complete-intersection period theorem of Villaflor Loyola.

The concrete advances within this research attempt are:

1. An exact global upper bound on the normalized weight sum of every invariant-column matrix candidate, with equality for the earlier degree-70 carrier.
2. A uniform obstruction showing that the earlier positive-anticanonical matrix criterion cannot cover all balanced Fermat packets, even with unbounded exponents and coordinate-power lifts.
3. Explicit complete-intersection surfaces, a uniform determinant identity, and nonzero exact periods for the infinite standard family missed by that criterion.

The original v0.1.0 archive is preserved byte for byte in `predecessor/`. Its original 24-check verifier was replayed successfully before this continuation. The geometric arguments of the predecessor have not been independently formally verified.

## 1. Conventions

Let

\[
X_m=\{F_m=x_0^m+\cdots+x_5^m=0\}\subset\mathbf P^5_{\mathbf C},
\qquad G_m=(\mu_m)^6/\mu_m.
\]

Write \(\langle r\rangle_m\) for the least-positive residue of a nonzero residue class. A full-support character is

\[
a=(a_0,\ldots,a_5),\qquad 0<a_i<m,\qquad \sum a_i\equiv0\pmod m.
\]

The Griffiths residue basis of the Fermat hypersurface diagonalizes the action of \(G_m\). The monomial \(x_0^{a_0-1}\cdots x_5^{a_5-1}\) at pole order three gives the character of middle Hodge type when \(\sum a_i=3m\). The entire rational orbit has type \((2,2)\) when

\[
\sum_i\langle ta_i\rangle_m=3m
\quad\text{for every }t\in(\mathbf Z/m\mathbf Z)^\times.
\tag{1.1}
\]

A rational packet is the rational subrepresentation whose complexification is the sum of these distinct conjugate eigenlines. An individual complex eigenvector is not being identified with an individual rational class.

The Jacobian ideal and socle monomial are

\[
J_{F_m}=(x_0^{m-1},\ldots,x_5^{m-1}),\qquad
S_m=\prod_{i=0}^5x_i^{m-2}.
\tag{1.2}
\]

We use

\[
\Omega=\sum_{i=0}^5(-1)^ix_i\,dx_0\wedge\cdots\widehat{dx_i}\cdots\wedge dx_5
\]

and the residue normalization of Villaflor Loyola, Theorems 1.1 and 1.2. The order of polynomial rows in each Jacobian below is explicitly fixed.

## 2. The matrix capacity and a certificate over an infinite set

Fix a character \(a\) modulo \(m\). Its invariant exponent columns form

\[
\mathcal L_a=\{v\in\mathbf Z_{\ge0}^6\setminus\{0\}:a\cdot v\equiv0\pmod m\}.
\]

Define

\[
C(a)=\sup\left\{\sum_vw_v:
\sum_vw_vv=\mathbf1,\quad w_v\ge0,
\quad\text{only finitely many }w_v\ne0\right\}.
\tag{2.1}
\]

Every nonsingular nonnegative integral matrix \(A\) satisfying \(A^Ta\in m\mathbf Z^6\), with \(w=A^{-1}\mathbf1>0\), gives one feasible point. Hence

\[
\mathbf1^TA^{-1}\mathbf1\le C(a).
\tag{2.2}
\]

This is a necessary numerical bound, not a sufficient geometric criterion. A capacity maximizer can use fewer than six columns. A six-column maximizer can fail normality or well-formedness. No claim about a normal carrier follows merely from \(C(a)>1\).

### Lemma 2.1: global dual certificate

Suppose \(y\in\mathbf Q_{>0}^6\) and \(y\cdot v\ge1\) for every \(v\in\mathcal L_a\). Then

\[
C(a)\le y\cdot\mathbf1.
\]

Indeed,

\[
\sum_vw_v\le\sum_vw_v(y\cdot v)
=y\cdot\sum_vw_vv=y\cdot\mathbf1.
\]

The infinitely many inequalities can be certified by a finite residue graph. Write \(y_i=c_i/L\), where \(c_i,L\) are positive integers. On \(\mathbf Z/m\mathbf Z\), an edge \(r\to r+a_i\) has cost \(c_i\). An integer function \(d\) satisfying

\[
d(0)=0,\qquad d(r+a_i)\le d(r)+c_i,
\qquad d(-a_i)+c_i\ge L
\tag{2.3}
\]

for every \(r,i\) certifies the dual inequality for **every** invariant column, regardless of its total degree.

To prove this, order the multiset described by a nonzero invariant column into a nonempty zero-sum word. Repeated application of the first inequalities bounds the cost of its prefix below by \(d(-a_i)\), where \(i\) is its last letter. Adding the last cost gives at least \(L\). Divide by \(L\).

The program uses a shortest-path algorithm to find a potential, but verifies (2.3) directly. The correctness of the global conclusion therefore depends on the displayed finite inequalities and this proof, not on trusting a shortest-path implementation or a search-degree cutoff.

### Proposition 2.2: the old degree-70 carrier is globally optimal in normalized weight sum

For

\[
a=(1,20,24,42,61,62)\pmod{70},
\]

take

\[
y=\frac1{70}(11,10,19,14,6,17).
\tag{2.4}
\]

The exact potential in `results/capacity_certificates.json` verifies all 420 edge inequalities in (2.3), and all six last-edge lower bounds are exactly 70. Thus

\[
C(a)\le\sum_i y_i=\frac{11}{10}.
\]

The matrix from v0.1.0 is

\[
A=\begin{pmatrix}
0&0&2&0&0&3\\
0&0&1&2&7&0\\
1&0&2&2&0&1\\
0&5&0&0&0&0\\
0&0&0&2&0&3\\
3&0&0&0&0&0
\end{pmatrix},
\quad
A^{-1}\mathbf1=(1/3,1/5,1/10,1/10,1/10,4/15).
\]

It is feasible and its weights sum to \(11/10\). Therefore

\[
\boxed{C(1,20,24,42,61,62\bmod70)=11/10.}
\tag{2.5}
\]

This is global within the invariant-column matrix model, not merely optimal among columns of degree at most 18. It is not an assertion that a scale-dependent anticanonical index has an invariant maximum.

## 3. A uniform obstruction to universal matrix-carrier coverage

For \(q\ge2\) and \(1\le b<q\), set

\[
m=5q,\qquad
 a_{q,b}=(b,b+q,b+2q,b+3q,b+4q,5(q-b)).
\tag{3.1}
\]

### Lemma 3.1: balance

Every character in (3.1) is full support and its rational orbit is of type \((2,2)\).

Let \(t\) be a unit modulo \(5q\), and let \(b'=tb\bmod q\), with \(1\le b'<q\). Multiplication by \(t\) permutes the five residues in the fiber over \(b'\), because \(t\) is a unit modulo 5. The first five least-positive residues are therefore, in some order,

\[
b',b'+q,b'+2q,b'+3q,b'+4q.
\]

The last residue is \(5(q-b')\). Their sum is \(15q=3m\). This is a proof for all parameters, separate from the finite checks in the bundle.

### Theorem 3.2: no positive-anticanonical invariant-column matrix

Assume \(q>5\) and \(\gcd(b,q)=1\). For every nonsingular nonnegative integral matrix \(A\) such that

\[
A^Ta_{q,b}\in5q\mathbf Z^6,
\qquad w=A^{-1}\mathbf1>0,
\]

one has

\[
\boxed{\sum_j w_j\le1.}
\tag{3.2}
\]

In fact \(C(a_{q,b})=1\).

**Proof.** Define

\[
y_q=\frac1q(1,1,1,1,1,q-5),\qquad y_q\cdot\mathbf1=1.
\]

If \(v\in\mathcal L_{a_{q,b}}\), reduction modulo \(q\), followed by cancellation of the unit \(b\), gives

\[
v_0+v_1+v_2+v_3+v_4-5v_5\equiv0\pmod q.
\]

Hence

\[
N=v_0+v_1+v_2+v_3+v_4+(q-5)v_5
\]

is divisible by \(q\). It is a positive integer because \(v\ne0\) and \(q>5\). Therefore \(N\ge q\), or \(y_q\cdot v\ge1\). Lemma 2.1 proves \(C(a_{q,b})\le1\).

Conversely \(v=\mathbf1\) is invariant, because \(\sum a_i=3m\), and putting weight 1 on it is a feasible point of (2.1). Thus \(C(a_{q,b})=1\), proving (3.2). \(\square\)

The invariant column set is unchanged by multiplying a character by a unit modulo \(m\), or by replacing \((m,a)\) by \((km,ka)\). A coordinate permutation merely permutes the columns' entries and the dual costs. Consequently none of these changes evades the obstruction.

For example, at degree 35 the packet is \((1,8,15,22,29,30)\), and the dual is \((1,1,1,1,1,2)/7\). No increase in exponent-search bounds can produce a matrix of the earlier type with normalized weight sum greater than 1.

**Interpretation.** This disproves universal applicability of the specific positive-anticanonical matrix criterion proposed in v0.1.0. It does not disprove the Hodge conjecture, exclude other uniruled carriers or correspondences, or exclude non-anticanonical approaches.

## 4. An actual cycle for the missed family

The construction now bypasses the carrier model entirely.

Fix \(q\ge2\), put \(m=5q\), and choose \(\kappa\in\mathbf C\) with

\[
\kappa^q=-1/5.
\]

Set

\[
z=x_5,\quad t_i=x_i^q\ (0\le i\le4),\quad P=x_0x_1x_2x_3x_4,
\]

and let \(e_j\) be the elementary symmetric polynomial of degree \(j\) in \(t_0,\ldots,t_4\). Define

\[
\boxed{
Z_\kappa=\{e_1=0,\ e_2=0,\ P-\kappa z^5=0\}\subset\mathbf P^5.
}
\tag{4.1}
\]

### Proposition 4.1: containment in the Fermat fourfold

Newton's identity is

\[
p_5=e_1(e_1^4-5e_1^2e_2+5e_1e_3+5e_2^2-5e_4)-5e_2e_3+5e_5.
\tag{4.2}
\]

Since \(e_5=P^q\), on \(Z_\kappa\) one has

\[
F_m=p_5+z^{5q}=5P^q+z^{5q}
=(5\kappa^q+1)z^{5q}=0.
\]

Thus \(Z_\kappa\subset X_{5q}\). Its defining equations have degrees \(q,2q,5\).

### Proposition 4.2: the surface is an integral complete intersection

Let

\[
S_q=\{e_1(x_0^q,\ldots,x_4^q)=e_2(x_0^q,\ldots,x_4^q)=0\}\subset\mathbf P^4.
\]

The coordinate-power map to the \(t\)-space is finite, so the dimension is two. In characteristic zero, on \(e_1=0\) the equations are equivalent to

\[
\sum x_i^q=0,\qquad\sum x_i^{2q}=0.
\]

At a hypothetical failure of Jacobian rank, there would be constants \(\lambda,\mu\), not both zero, such that for each nonzero coordinate

\[
\lambda+2\mu x_i^q=0.
\]

The case \(\mu=0\) is impossible. Otherwise all nonzero \(x_i^q\) equal the same nonzero constant. Their sum cannot vanish in characteristic zero. Thus \(S_q\) is smooth. It is a connected complete intersection of positive-dimensional ample divisors, hence irreducible.

The same argument with four coordinates shows that \(S_q\cap\{x_i=0\}\) is a smooth reduced complete-intersection curve. Distinct such curves share no irreducible component, since imposing two coordinate zeros gives a zero-dimensional intersection. In particular the divisor of \(P\) has valuation one at the generic point of each coordinate curve.

Forgetting \(z\) defines a finite flat cover \(Z_\kappa\to S_q\) of degree five. On a chart trivializing \(\mathcal O_{S_q}(1)\), its equation is \(z^5=P/\kappa\), with the corresponding trivializations understood. At a generic coordinate curve its right side has valuation one. The degree-five polynomial is Eisenstein over that discrete valuation ring and is therefore irreducible over the function field of \(S_q\). Finite flatness makes the cover generically integral without vertical or embedded components; locally its monic algebra injects into the generic field extension. Hence the cover is integral.

The two equations of \(S_q\), followed by the monic equation in \(z\), form a homogeneous regular sequence. The resulting projective ideal is saturated and defines the integral complete intersection (4.1). Therefore

\[
\dim Z_\kappa=2,\qquad\deg Z_\kappa=q(2q)5=10q^2.
\]

The surface need not be smooth. Villaflor Loyola's complete-intersection theorem does not impose smoothness of \(Z\); its proof explicitly reduces to a smooth perturbation. We use this version, not an unverified smooth-cycle variant.

## 5. The exact Jacobian determinant

Define

\[
\begin{aligned}
f_1&=e_1,&g_1&=e_1^4-5e_1^2e_2+5e_1e_3+5e_2^2-5e_4,\\
f_2&=e_2,&g_2&=-5e_3,\\
f_3&=P-\kappa z^5,&g_3&=5\sum_{j=0}^{q-1}P^{q-1-j}\kappa^jz^{5j}.
\end{aligned}
\]

The geometric-series identity and (4.2) give

\[
F_m=f_1g_1+f_2g_2+f_3g_3.
\tag{5.1}
\]

Let

\[
H=(f_1,g_1,f_2,g_2,f_3,g_3),\qquad
D_\kappa=\det\operatorname{Jac}_{(x_0,\ldots,x_4,z)}H,
\]

and

\[
\Delta(t)=\prod_{0\le i<j\le4}(t_i-t_j).
\]

### Theorem 5.1: uniform determinant formula

\[
\boxed{
D_\kappa=625q^5\Delta(x_0^q,\ldots,x_4^q)
\sum_{b=1}^{q-1}\kappa^{q-b}P^{b-1}z^{5(q-b)-1}.
}
\tag{5.2}
\]

**Proof.** First,

\[
df_1\wedge dg_1\wedge df_2\wedge dg_2
=25\,de_1\wedge de_2\wedge de_3\wedge de_4.
\tag{5.3}
\]

Only the term \(-5de_4\) in \(dg_1\) survives after wedging with \(de_1,de_2,de_3\); the row permutation has positive sign.

Next, direct differentiation yields

\[
df_3\wedge dg_3=
25q\sum_{j=1}^{q-1}\kappa^jP^{q-1-j}z^{5j-1}\,dP\wedge dz.
\tag{5.4}
\]

For each interior index \(j\), the two contributing coefficients add to \(j+(q-j)=q\). The endpoint terms have zero derivative coefficient. Thus (5.4) is an identity for every positive integer \(q\), not an interpolation from checked values.

Finally,

\[
de_1\wedge\cdots\wedge de_5
=\Delta(t)\,dt_0\wedge\cdots\wedge dt_4.
\]

Use \(e_5=P^q\) and \(dt_0\wedge\cdots\wedge dt_4=q^5P^{q-1}\,dx_0\wedge\cdots\wedge dx_4\). Cancellation in the polynomial ring gives

\[
de_1\wedge\cdots\wedge de_4\wedge dP
=q^4\Delta(x^q)\,dx_0\wedge\cdots\wedge dx_4.
\tag{5.5}
\]

Combining (5.3), (5.4), and (5.5), and putting \(b=q-j\), proves (5.2). The identity extends across \(P=0\) because it is a polynomial identity. \(\square\)

The degree of every monomial in (5.2) is \(15q-6=3m-6\), as required for a middle residue numerator.

## 6. Nonzero periods, not just a formal character match

Fix \(1\le b<q\). In the order used in (3.1), the coefficient of

\[
x_0^{b-1}x_1^{b+q-1}x_2^{b+2q-1}x_3^{b+3q-1}x_4^{b+4q-1}
 z^{5(q-b)-1}
\tag{6.1}
\]

in \(D_\kappa\) is

\[
625q^5\kappa^{q-b}\ne0.
\tag{6.2}
\]

All permutations of the first five exponents have the same nonzero magnitude, with the Vandermonde sign. Different values of \(b\) and different permutations give different monomials. Every exponent lies between zero and \(m-2\), so no term is killed by the Fermat Jacobian ideal.

Define the dual numerator

\[
Q_b=\prod_{i=0}^5x_i^{m-a_{q,b,i}-1}.
\tag{6.3}
\]

It has degree \(3m-6\). Because the product \(Q_bD_\kappa\) has socle degree, a surviving monomial modulo \(J_{F_m}\) must have all six exponents equal to \(m-2\). Formula (6.1) is the unique term with this complement. Therefore

\[
Q_bD_\kappa\equiv625q^5\kappa^{q-b}S_m\pmod{J_{F_m}}.
\tag{6.4}
\]

For the Fermat polynomial,

\[
\det\operatorname{Hess}(F_m)=[m(m-1)]^6S_m.
\]

Apply Villaflor Loyola's Theorem 1.2 with dimension four and the ordering fixed above. Its constant is

\[
c=\frac{625q^5\kappa^{q-b}}{[m(m-1)]^6}.
\]

The exact period is consequently

\[
\boxed{
\int_{Z_\kappa}\operatorname{res}\left(\frac{Q_b\Omega}{F_m^3}\right)
=\frac{(2\pi i)^2}{50q}\,\kappa^{q-b}\ne0.
}
\tag{6.5}
\]

The normalization follows from \(625q^5/[2(5q)^6]=1/(50q)\). In conventions using a differently normalized residue map, the displayed constant changes with that convention; nonvanishing does not.

### Rational algebraicity of whole packets

Let \(h\) denote the hyperplane class. Since \(\deg Z_\kappa/m=2q\), the primitive part

\[
\xi_\kappa=[Z_\kappa]-2q h^2
\]

is rational and algebraic. Villaflor Loyola's Theorem 1.1 identifies its primitive residue numerator with \(-2D_\kappa/m\). Thus its complex eigenspace support consists of exactly the \(120(q-1)\) characters obtained from (3.1) by permuting the first five entries and varying \(b\).

That set is closed under multiplication by units modulo \(m\), by Lemma 3.1. Each of its eigenspaces has dimension one. The \(\mathbf Q[G_m]\)-submodule generated by \(\xi_\kappa\) therefore has complexification equal to the entire sum of those eigenlines: applying the complex character idempotents isolates each nonzero component. Since the generator and the group action are rational, this is the complexification of the claimed rational submodule.

Every vector in that rational submodule is a rational linear combination of classes of diagonal translates of \(Z_\kappa\) and of \(h^2\). Hence every rational packet in the family is algebraic. Its rational algebraic subspace has dimension

\[
120(q-1)
\]

for this fixed choice of the last coordinate. This is not the dimension of all Hodge classes on \(X_{5q}\).

The conclusion recovers Aoki's standard family, including the elementary decomposable midpoint case at even levels. It does not close arbitrary nonstandard five-primary packets.

## 7. A concrete example at degree 35

Take \(q=7\), \(b=1\), \(\kappa^7=-1/5\). Then

\[
a=(1,8,15,22,29,30),\quad
Z_\kappa=\left\{
\begin{array}{l}
\sum_{i=0}^4x_i^7=0,\\
\sum_{0\le i<j\le4}x_i^7x_j^7=0,\\
x_0x_1x_2x_3x_4=\kappa x_5^5
\end{array}\right\}\subset X_{35}.
\]

The cycle has degree 490. The rational packet has dimension \(\varphi(35)=24\), since its first character entry is 1. The determinant coefficient is

\[
10,504,375\,\kappa^6.
\]

For

\[
Q_1=x_0^{33}x_1^{26}x_2^{19}x_3^{12}x_4^5x_5^4,
\]

one obtains

\[
\boxed{
\int_{Z_\kappa}\operatorname{res}\left(\frac{Q_1\Omega}{F_{35}^3}\right)
=\frac{(2\pi i)^2\kappa^6}{350}\ne0.
}
\]

At the same time, Theorem 3.2 proves that this packet has capacity exactly 1 and cannot use the positive-anticanonical matrix route. Thus this is an explicit example where failure of that constructor is compatible with, and bypassed by, an actual algebraic cycle.

At degree 70 the standard packet \((1,15,29,43,57,65)\) obtained by setting \(q=14\) is **different** from the earlier packet \((1,20,24,42,61,62)\). Their capacities are respectively 1 and \(11/10\). They must not be conflated.

## 8. Exact computations and limitations

The final verifier uses integers, rational numbers, and symbolic polynomial identities. It uses no floating-point arithmetic, random sampling, network request, or optimization routine.

Its 137 grouped assertions include:

- balance and exact primal/global-dual certificates for seven specified packets;
- the predecessor archive checksum;
- Newton's identity and the elementary-symmetric Jacobian identity;
- exact six-by-six intermediate determinants for \(q=2,3,4,5,7,11,17\);
- independent socle-pairing checks for every \(b\) at \(q=2,7,11\);
- all \(b\), all units, and all first-five permutations for \(2\le q\le64\), totaling 241,920 distinct support monomials and 218,836 balance/conjugacy instances.

The seven globally certified capacity values are:

| Modulus | Character | Capacity |
|---|---|---|
| 25 | (1,6,11,16,20,21) | 6/5 |
| 33 | (1,4,16,22,25,31) | 2 |
| 35 | (1,8,15,22,29,30) | 1 |
| 39 | (1,7,16,22,34,37) | 2 |
| 40 | (1,9,17,25,33,35) | 1 |
| 55 | (1,12,23,34,45,50) | 1 |
| 70 | (1,20,24,42,61,62) | 11/10 |

These are seven specified inputs, not a census of all characters at those levels. Capacities 2 in the table do not themselves supply a six-column normal carrier.

The finite identities support the implementations. The all-parameter assertions come from the separate mathematical proofs in Sections 3–6, conditional only on the stated standard algebraic-geometric and residue theorems. These proofs remain at manuscript level.

### Unclosed targets

No proof is given of the general Hodge conjecture, of coverage of every Fermat packet, of the full CM half-twist Chow correspondence, or of the earlier central-defect realization lemma. The universal positive-anticanonical invariant-matrix conjecture is false by Theorem 3.2 and should not remain in a gap ledger as an unproved plausible universal lemma.

The usable research architecture is now a collection of separately certified constructors: carrier transfer where its hypotheses hold, explicit standard surfaces where the capacity barrier is 1, and other correspondences for packets not handled by either route. A proof that such constructors exhaust all Hodge classes is still missing.

## References

See `SOURCES.md` for exact versions, theorem locators, extraction boundaries, failed retrievals, and the notation translation.

- R. Villaflor Loyola, *Periods of complete intersection algebraic cycles*, arXiv:1812.03964v5, 30 March 2021, Theorems 1.1 and 1.2.
- R. Jumagulov, *The Hodge conjecture for Fermat fourfolds of odd degree at most 199*, arXiv:2608.18134v1, Proposition 1.9 and its even-degree discussion. Used for known-family identification, not as a verified computational census.
- N. Aoki, *Some new algebraic cycles on Fermat varieties*, J. Math. Soc. Japan 39 (1987), 385–396. Historical attribution via the checked later source; original full text not successfully obtained in this session.
- The geometric dependencies of the prior carrier theorem remain in the preserved v0.1.0 proof; no new proof of them is claimed here.
