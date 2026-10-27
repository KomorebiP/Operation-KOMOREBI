# Actual source contact and its exterior cancellation

Base: Euler-Bernoulli-structure-20261005, archive SHA256
b1dd12d9e0904b7d9a0b999e961fd1b12b4e3afde71995da4064d7849cdfacf7.
All quantifiers below concern admitted ordinary T>=0,
r=(17659+2^18 T)2^640-161, with true terminal161. No parent proof is modified.
The actual Euler nonvanishing target remains open.

The basic source elimination is already proved in
`next/unit_identity/epsilon_critical_manifold.md`, equations5-9. The new
attempt was the following arithmetic strengthening: use a strictly leading
exterior coordinate of the actual two scaled Newton tails to prevent their
logarithmic derivative from equalling log9. This note retains the diagonal
logarithmic term and computes that proposed comparison exactly. Its two sides
have the same valuation and the same leading unit. The complete mismatch has
a unique zero on every actual chart, so a bound excluding its zero everywhere
on the chart would be false for the actual family, not just for a free model.

## 1. Exact objects, derivatives, and the exterior pairing

Write x=10202+2^15 Z, Q(x)=(x+1)(2x+1), and L=log9. Put

    a_0(x)=gamma_0,
    a_q(x)=Q(x) gamma_q P_(q-1)(x), q>=1,
    U(x)=sum_(q>=0) 9^-q a_q(x),
    V(x)=sum_(q>=0) a_q(x).

Here the gamma_q are the prescribed actual Bernoulli packet coefficients.
They are not varied. The exact source identity is

    P_q(x)A(x-q)=P_(q-1)(x)(9^(x-q+1)-1)/8, q>=1,
    8QG=9^(x+1)U-V.                                    (1)

At fixed ordinary r the coefficient bounds give restricted convergence of
these sums and their derivatives. All derivatives without a Z subscript are
ordinary x derivatives. On this chart U,V have valuation153 and their
normalized versions

    u=2^-153 U, v=2^-153 V

are restricted analytic units. Define

    F=9^(x+1)u/v-1,
    M=L+u'/u-v'/v,
    W=UV'-U'V-LUV.                                      (2)

Exactly, M=F'/(1+F) and W=-UV M. The double-root equations for G are
F=M=0, with no common-zero denominators. The pairing is

    W=sum_(i<j) (9^-i-9^-j)(a_i a_j'-a_i' a_j)-LUV.      (3)

The double series converges and rearrangement is legitimate. The final term
in (3) is not an exterior minor and may not be deleted. In particular no
Hankel determinant formula has been substituted for the entire W.

## 2. Actual arithmetic defeats the first strict exterior comparison

Set v_q=2^-153 a_q and d_q=2 v_q'. The d_q are integral restricted functions
on the chart, despite some individual v_q' having valuation-1. Let

    W_geo=UV'-U'V,
    X_(ij)=(9^-i-9^-j)(v_i d_j-d_i v_j).

Thus 2^-305 W_geo=sum_(i<j) X_(ij), and the logarithmic term after the
same normalization is2Luv. Uniformly on the entire actual chart,

    v2(X_(0,161))=4, X_(0,161)/2^4=3 mod8,
    v2(X_(0,1))=5,   X_(0,1)/2^5=1 mod8,
    sum_(i<j, (i,j) not (0,161),(0,1)) X_(ij) in2^8 Z_2<Z>.
                                                               (4)

Consequently the precise comparison is

    v2(W_geo)=v2(LUV)=309,
    W_geo/2^309 = LUV/2^309 =5 mod8.                     (5)

This is an actual Bernoulli-unit statement, not a valuation-only surrogate.
It disproves the proposed unique-minimum argument against the complete W.

Here are the low-unit and tail details. The inherited actual units are

    gamma_0=2^154, gamma_1/2^153=43 mod64,
    gamma_161=7 mod8, v2(gamma_2)=157,
    v2(gamma_q)>=149+3q, 3<=q<161,
    v2(gamma_(161+t))=3t+s2(t), 1<=t<2^640.

All gamma_q are integral at every index. At x=90+128a, a=79+256Z is odd,

    v2(P_160)=159,
    P_160'/2^152=3 mod8.                                (6)

For the second congruence, remove the factor x-90. At x=90 the remaining
falling product has normalized odd part
-odd(90!)odd(69!)=-5*5=7 mod8. Moving to90+128a contributes5 mod8 from
the paired differences±64. All other pairs and the unpaired differences
70,...,90 contribute1 mod8. The derivative correction from that removed
factor is1 mod8: the±64 pair contributes8a^2/(4a^2-1), the smaller pairs
and the unpaired differences are also divisible by8. The odd-factor
product is1 mod8, and its derivative correction is more divisible. This
proves (6) coefficientwise on the affine chart.

Since Q=7, Q'=3 mod8, the resulting jets are

    v_0=2, d_0=0,
    v_1=5 mod8, d_1/2=1 mod8,
    v2(v_161)=6, d_161=3 mod8.

Also v2(v_2),v2(d_2)>=5; for q=3 these bounds are at least6; for4<=q<161
both are at least3q-3. At q=162 the corresponding bounds are11 and5.
For q>=163 before the next carry they are at least13 and7. These bounds
are coefficientwise on the chart: P_161 and P_162 have local Gauss
valuation160 and their ordinary derivatives have Gauss valuation153.
For larger n, factor P_n=P_162 times the remaining integral factors.
Before the next carry the scalar gains at least7. Beyond that carry the
remaining falling factors supply at least one additional factor2 in every
two factors, also coefficientwise; an ordinary derivative removes at most
one of these factors2. Their number is enormous, so the same bounds hold
even when only gamma_q integrality is used. These estimates,
together with

    v2(9^-i-9^-j)=3+v2(i-j), i!=j,

give (4), including all pairs. The weights of the two retained pairs satisfy
(1-9^-161)/8=1 mod8 and (1-9^-1)/8=1 mod8. Finally

    u=v=7 mod8,    2u'=2v'=5 mod8,    L/8=5 mod8,

where the derivative congruences concern the normalized u,v. The first two
pair contributions give3+2=5 mod8; the logarithmic term gives the same5.

## 3. The complete mismatch has an actual zero on every chart

Put

    K=2^-178 G,
    B=Q/v,
    A_crit=K_Z/2,
    D=B_Z/(2B).

The letter A_crit here denotes the half derivative, not the source A.
The inherited chart theorem states that A_crit is an isometry of Z_2 with
unique zero c, K_ZZ/2=1 mod8, and unit quadratic stationary-distance law.
The actual arithmetic above gives

    2 B'/B = 2Q'/Q-2v'/v =7 mod8,
    D in2^13 Z_2<Z>, D/2^13=7 mod8.                     (7)

For coefficientwise integrality, v_Z has Gauss valuation14: the unique
leading packet is161, with ordinary derivative valuation152 before division
by2^153, followed by the Z scale2^15. Q_Z has valuation15. The normalized
local factors used in (6) give the same bound and unit coefficientwise;
all remaining packets are more divisible. Since B is a restricted unit,
(7) follows as a restricted-series statement, not just pointwise.

Equation (1) now reads F=2^28 BK. Differentiating gives

    M=2^14 B/(1+F) [A_crit+D K].                         (8)

Define J=A_crit+D K. Because D is coefficientwise divisible by2^13, J
has the same affine unit reduction as A_crit. Thus J is an isometry and
has exactly one zero zeta in Z_2. It is also the unique zero of M and W.
This proves that unconditional mismatch nonvanishing on this actual chart
is false; that proposed inequality cannot serve as the missing theorem.

At the actual Euler stationary point c, write Phi=K(c). Isometry in (8)
and (7) give the exact center-distance law

    v2(zeta-c)=13+v2(Phi).                              (9)

The equality uses infinity on both sides if Phi=0. When Phi is nonzero,
stationarity gives

    v2(K(zeta)-Phi)=2v2(zeta-c)=26+2v2(Phi)>v2(Phi),
    v2(F(zeta))=28+v2(Phi).                             (10)

Thus the new contact center does not lose the unknown critical scalar.
It provides no independent upper bound for its valuation.

The complete exterior at the actual c has the stronger unit identity

    W(c)=2^333 Theta(c) Phi,
    Theta= -u Q (D/2^13)/(1+F),  Theta=1 mod8.            (11)

In particular all the cancellation between the nonzero terms in (5) can
persist: their difference has valuation333+v2(Phi). The first24 bits of
relative cancellation are automatic on the actual stationary chart.
The remaining cancellation in (11) is exactly the unresolved arithmetic
quantity. No inference from ordinary stationarity to shifted or coefficient
stationarity has been made.

## 4. Cheapest exact discriminator and precision

`check_source_contact.py` uses only the three already fixed ordinary T values
0,718787533,22831001499602523078606181325. It independently rebuilds U and V
from their source-free packets, builds the full exterior polynomial including
log9, and lifts its zero independently of the lift of K_Z/2. The results are:

| T | v2(Phi) | v2(zeta-c) | v2(W(c)) | v2(F(zeta)) |
|---|---:|---:|---:|---:|
| 0 | 0 | 13 | 333 | 28 |
| 718787533 | 30 | 43 | 363 | 58 |
| 22831001499602523078606181325 | 91 | 104 | 424 | 119 |

In every case the two retained exterior pairs and the logarithmic term have
the exact valuations and units in (4)-(5). No parameter search is performed.
The result at zeta is a nonzero source value in these fixed cases; zeta is
not an Euler double zero.

Global coefficient precision is384 bits. The scalar cutoff
floor((384+s2(r)-156)/3) makes all omitted gamma coefficients zero modulo
2^384, also after ordinary differentiation. Affine degrees above25 vanish
because the chart slope is2^15. Dividing U,V by2^153 leaves231 bits; forming
twice their ordinary derivatives divides their Z derivatives by2^14, leaving
217 bits. The exterior is computed at200 normalized bits and is coefficientwise
divisible by2^15, leaving185 bits for its zero. The actual K is known to206
bits and its center to205 bits. These exceed every displayed distance and
value valuation. The actual center-substitution error in the exterior is at
least15+205=220 normalized bits, above200. The independently lifted exterior
center has error2^185; F_Z is divisible by2^29 and vanishes at the true
exterior center, so its value is stable well past200 bits. The units shown in
the table and the low-unit comparisons are therefore about the true analytic
centers, not just insufficient representatives. Zero residues are not promoted
to exact zero statements.

## 5. Exact missing implication

The actual leading exterior coordinate is controlled and nonzero. The log9
term has the same valuation and cancels it; the whole mismatch has a unique
actual zero on the chart. To exclude Euler double contact one must prove
zeta!=c, equivalently F(zeta)!=0. Equation (11) shows why bounding W(c) by
reusing G's stationary value would be circular. No independent Bernoulli
Newton/Stirling inequality separating these two centers was obtained.

The weighted/reciprocal route in
`shifted_obstruction/weighted/RECIPROCAL_CUTOFF_AND_ACTUAL_COMMUTATOR.md`
already explains why its finite cutoff identity does not close an ordinary
x-differential equation. This attempt does not repeat that elimination or
delete its commutator. It tests a different precise inequality—the proposed
strict dominance of the exterior part over the logarithmic term—and proves
that inequality false for the prescribed actual coefficients. Neither the
new zero of M nor the equal-leading-term calculation is an Euler counterexample.
