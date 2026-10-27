# Ordinary-index quadratic compression and its arithmetic boundary

Status: proved degree-two compression and exact discriminant transfer; the
ordinary-index nonintersection theorem remains unproved. This is a new
construction reducing the precision-height deficit from quadratic to linear.
The surviving linear constant is too large to establish the desired separation.

## 1. Fixed actual Euler input

Fix one admitted ordinary index

    r=(17659+2^18 T)2^640-161, T>=0,

with true terminal161. Let f(Z)=K_r(Z) be the actual Euler function on
x=10202+2^15 Z. The inherited complete coefficient theorem gives

    f(Z)=a+2bZ+uZ^2+256 Z^3 R(Z),
    a,b in Z_2, u in Z_2^*, R in Z_2<Z>.

There is a unique critical point c in Z_2, and Phi=f(c). In particular,
f'/2 is a dyadic isometry and c is controlled by complete coefficient
approximations to f. Nothing below interpolates T. All tails are retained
through those coefficientwise approximation theorems.

The actual correction is at E=2r-25 relative to the depleted member.
The construction here applies directly to the actual f. It also applies to
the depleted member when that member has the same inherited quadratic class.
It does not identify the two members' prepared quadratic coefficients.

## 2. A quadratic factor at every precision

There are unique W=Z^2+2 beta Z+alpha and U in Z_2<Z> such that

    f=U W,  U=u (mod256),  W=u^(-1)(a+2bZ+uZ^2) (mod256).       (1)

Here U is an analytic unit and beta,alpha are dyadic integers. This does not
assert that alpha or beta is rational, algebraic over Q, or of bounded rational
height.

For completeness, the following direct lifting proves (1). Normalize g=f/u.
At precision8 take W_8=g_0+g_1 Z+Z^2 modulo256 and V_8=1. Suppose

    g=V_k W_k (mod2^k),  deg W_k=2, W_k monic,
    V_k=1 (mod256), W_k=W_8 (mod256).

Reduce the complete residual (g-V_k W_k)/2^k modulo2. It is a finite
polynomial because g is restricted. Divide it by the monic quadratic
W_bar in F_2[Z], giving a quotient Q_k and remainder S_k of degree<2.
Set

    V_(k+1)=V_k+2^k Q_k,  W_(k+1)=W_k+2^k S_k.

Since V_k=1 modulo2, this kills the residual modulo2^(k+1). The corrections
preserve the prescribed reductions and the monic quadratic coefficient.
They converge in the Tate algebra, proving existence. For uniqueness,
subtract two factorizations at the first bit where they differ: uniqueness
of polynomial division forces both corrections to agree. The same argument
applies successively at every bit. Take U=u V.

Consequently complete f modulo2^P determines W modulo2^P with no loss of
precision. It does not require evaluating a large integer representative of
c or taking a resultant of a polynomial whose degree grows with P. A finite
input polynomial can be handled with polynomial arithmetic modulo2^P; its
cofactor degree is at most its degree minus two.

Although 2 beta modulo2^P only specifies beta modulo2^(P-1), the quantity

    delta=beta^2-alpha

is determined modulo2^P for P>=2. Replacing beta by beta+2^(P-1)t changes
its square by 2^P beta t+2^(2P-2)t^2.

## 3. Exact stationary-value/discriminant transfer

The reduced discriminant delta, rather than a root of a rational polynomial,
is the relevant scalar. Its relation with Phi is exact, including all unit
and derivative effects.

Put w=W(c) and tau=U'(c)/U(c). Then w=Phi/U(c) is integral and tau lies in
256 Z_2. Stationarity gives

    W'(c)=-tau w.

For every c, the quadratic identity is

    beta^2-alpha = W'(c)^2/4-W(c).

Therefore

    delta=-Phi/U(c) * [1-tau^2 Phi/(4 U(c))].                  (2)

The bracket is 1 modulo2^14. In particular,

    v2(delta)=v2(Phi),  Disc(W)=4 delta,                     (3)

with the convention v2(0)=infinity. This proves the transfer even when Phi
vanishes. It does not use an unproved assertion that the dyadic critical
point is algebraic or rational. The cofactor derivative is included.

At finite precision let A_P,B_P be the least nonnegative representatives of
alpha,2 beta modulo2^P. B_P is even. The integer

    d_P=(B_P/2)^2-A_P                                      (4)

satisfies d_P=delta modulo2^P. Thus v2(d_P)<P is a complete certificate for
v2(Phi)=v2(d_P). The assertion d_P!=0 as an ordinary integer is insufficient.

## 4. The improvement and the sharp surviving deficit

The old evaluation of a degree-O(P) rational polynomial at a P/2-bit
critical lift incurred an O(P^2) height term. Construction (4) reduces the
relevant polynomial degree to two and gives an integer of size

    |d_P| < 2^(2P-2)+2^P.

Thus its height has a linear upper bound, about2P bits. This is a genuine
degree reduction. It removes that particular quadratic-in-precision cost.
It does not imply |d_P|<2^P, the inequality needed to exclude a nonzero
integer divisible by2^P.

The factor two is not just loose bookkeeping. Consider the single fixed
rational polynomial

    f_*(Z)=(Z-1/3)^2.

It satisfies the same quadratic class with U=1 and has exact Phi_*=0. Its
integer quadratic representatives (4) are nonzero at every even P>=6. Put
M=2^P and

    C_P=10 if P=0 mod6; 4 if P=2 mod6; 7 if P=4 mod6.

Direct modular inversion of3 and9 gives

    d_P=M(M-C_P)/9,
    v2(d_P)=P+v2(C_P),
    bit_length(d_P)=2P-3.                                  (5)

Indeed B_P/2=(M-1)/3, and A_P=(1+(C_P-2)M)/9. These are their required
representatives. Formula(5) follows by substitution; for M>=64 the number
lies strictly between2^(2P-4) and2^(2P-3).

Hence fixed rational input, fixed degree two, exact derivative control,
nonzero finite integer discriminants, and linear height about2P are jointly
compatible with an identically zero limiting stationary scalar. This is an
obstruction to the proposed inference, not an Euler counterexample. Choosing
special rational representatives of f_* could recover its exact zero
discriminant; that only reinforces the need to prove nonzero separately.

## 5. A precise additional height statement that would suffice

A possible arithmetic improvement can now be stated without the large
approximation degree. Suppose actual Euler arithmetic supplied, for all
sufficiently large P, integers A,B,C with A odd such that

    A Z^2+2B Z+C = A W(Z) (mod2^P),
    0 < |B^2-A C| <= 2^(2 eta P+2 C(r)+1), eta<1/2.          (6)

For example the displayed bound follows from
max(|A|,|B|,|C|)<=2^(eta P+C(r)), together with the nonzero-discriminant
condition. Division by A is legal dyadically. Because the linear coefficient
is even, its congruence specifies B/A modulo2^(P-1), enough to compare its
square modulo2^P. Thus

    (B^2-A C)/A^2 = delta (mod2^P).

For any P>(2 C(r)+1)/(1-2 eta), inequality(6) is strictly below2^P. It then
forces v2(delta)<P and proves actual nonvanishing. This is a concrete
small-height quadratic construction sufficient for a depth-independent
bound. Neither the proven Hankel law nor the rationality of the ordinary
Bernoulli coefficients currently supplies (6). Our modular preparation has
eta=1; it misses the required threshold eta<1/2. A bound only on the integer
discriminant itself with slope<1 would also suffice.

Condition(6) is stated as the exact missing additional arithmetic input,
not as a theorem or a heuristic. Reconstructing a small nonzero rational
representative from an already nonzero residue would presuppose the desired
escape and is not a proof of it. Uniform bounded rational height of W itself
would be even stronger and would force its coefficients to be rational by
finiteness; no such transfer is assumed here.

For separation from the undepletion correction one would apply the same
construction to the depleted member and additionally need a certified escape
precision P<=E=2r-25. No estimate of C(r) accomplishing this follows from the
present argument. The actual quadratic construction does not require that
stronger comparison with E, but still requires a nonzero scalar certificate.

## 6. Bounded checks and provenance

The checker reads the already fixed complete94-bit actual Euler records
T=0 and T=718787533 from
`bernoulli_closure/separation/carry_adapted/inherited_actual.json`.
No new multiplier digits, new candidate values, or parameter extension are
computed. At precisions16,24,32,48,64,80,93 it constructs the entire unit
cofactor and quadratic, checks their coefficientwise product, checks
compatibility between precisions, and independently computes the critical
center from the actual f'/2. The reduced-discriminant and critical-value
valuations agree, capped at the available precision.

There are14 actual quadratic lifts. They recover the inherited valuations0
and30, without claiming additional universal coverage. For the second case,
P=16 and24 return zero residues and correctly do not certify nonvanishing;
P=32 returns valuation30. These distinguish integer nonzero discriminants
from valid nonzero residue certificates.

The same checker verifies the exact sharp-control formulas(5) for all even
P from6 through128,62 cases. The general formulas are proved above; the
finite checks are corroboration. Execution is exact integer arithmetic in
Python3.12.14. The experiment contract and recorded runner artifacts are
`contract.json` and `certified_run/{manifest.json,results.json}`.

The ordinary-index target remains open. The completed output is the
quadratic compression, exact formula(2), linear-height improvement, and
proved obstruction to inferring escape from that improvement alone.
