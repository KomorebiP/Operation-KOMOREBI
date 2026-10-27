# Radical-supported precision: exact certification and a discrete obstruction

Checkpoint ABC-20261025-RR8, continuing RR7 archive SHA-256
83c7020fd03361142fcac0567bd097c6b61c244f3a953c4618d13fd0cf4ead0a.
Owner: /root/rr8_precision. This route uses elementary integer arithmetic,
not IUT or an imported S-unit estimate. The target remains the every-epsilon
ordinary integer ABC bound. The results below do not establish that bound.

## 1. The declared finite view and its weighted precision

Let S be a finite nonempty set of primes and k_p>=1 for p in S. Put

    R=product_(p in S) p,
    M=product_(p in S) p^(k_p),
    L=log M=sum_(p in S) k_p log p.

The intended raw sources here are positive integer triples with pairwise
coprime coordinates and radical rad(abc)=R. Exact additive sources are
the subset with d(a,b,c)=a+b-c=0. At finite precision retain the coordinate
residues modulo M, the actual support labels, and the ordinary integer
coordinates as the common source. The finite coherence test is d=0
modulo M. This does not assert that every finite coherent view is an
exact additive source.

Equivalently use finite ring views modulo each p^(k_p), with coordinate
reductions and ordinary sum restrictions. CRT identifies their product
with the single view modulo M. Increasing k_p gives the declared
reduction to lower precision. Prime support is set-valued, not linear.

**Theorem 1 (weighted-precision exactness certificate).** For an integer
triple with c>0, put eta=|a+b-c|/c and h=log c. If

    a+b=c mod M,         exp(h) eta<exp(L),              (1)

then a+b=c as integers. Equivalently, a nonzero defect passing this
modular test must satisfy

    |d|>=M,              eta>=exp(L-h).                 (2)

If 0<a,b<=c, then |d|<=c. Thus c<M and the modular test already
imply exactness. At a supplied bound c<=B, eta<M/B also suffices.

*Proof.* The modular condition makes d an integer multiple of M. Every
nonzero multiple has absolute value at least M. Since c eta=|d|, this
proves (1)--(2). For positive a,b<=c the defect lies in (-c,c], proving
the remaining claims. QED.

Strict inequality is necessary in the general certificate: a defect M
is modularly zero and nonzero as an integer. The theorem does not build
B from R. It states the exact interaction of local precision, an
archimedean residual and an independently supplied height bound. Uniform
k_p=N gives threshold M=R^N.

## 2. Arbitrarily deep supported congruences at fixed radical

**Theorem 2.** For every integer N>=4 there are integers u,v,w>=N with

    a=4^u,             b=9^v,             c=25^w,
    c>a+b,             a+b=c mod 30^N.                  (3)

For each fixed N, c can be arbitrarily large. All coordinates are
pairwise coprime, with exactly rad(abc)=30, and d is nonzero. Hence
no finite function F(R,N) bounds log c on all positive pairwise-coprime
raw triples of radical R with c>=max(a,b) and a+b=c modulo R^N.

### Elementary unit-group fact

For an odd prime p and g=1+p^s q with s>=1 and p not dividing q,

    v_p(g^k-1)=s+v_p(k),       k>=1.                    (4)

The same statement holds for p=2 if s>=2 and q is odd. To prove it,
first use the geometric sum to see that an exponent prime to p leaves
v_p(g-1) unchanged. Raising to p increases this valuation by exactly
one: the first nonconstant binomial term has valuation s+1 and all
later terms have larger valuation under the stated conditions.
Iteration proves (4), including the p=2 case under s>=2.

Modulo p^N with N>=s, such a g has order p^(N-s). Its powers fill
the subgroup of units equal to 1 modulo p^s, which has that same size.
The required instances are

    <9>  modulo 2^N = {units equal to 1 modulo 8},
    <4>  modulo 3^N = {units equal to 1 modulo 3},
    <16> modulo 5^N = {units equal to 1 modulo 5}.        (5)

### Exponent construction

By (5), choose residues ell_2,ell_3,r_5 with

    9^(ell_2)=25  modulo 2^N,
    4^(ell_3)=25  modulo 3^N,
    16^(r_5)=-9   modulo 5^N.                           (6)

Their respective moduli are 2^(N-3),3^(N-1),5^(N-1).
Since 9 and 25 are both 9 modulo 16, ell_2 is odd when N>=4.

Choose u,v,w satisfying

    u=ell_3  modulo 3^(N-1),
    u=2 r_5  modulo 2*5^(N-1),

    v=ell_2  modulo 2^(N-3),
    v=1      modulo 2*5^(N-1),

    w=1      modulo 2^(N-3)*3^(N-1).                    (7)

The u moduli are coprime. The v conditions agree modulo their common
divisor 2 because ell_2 is odd. Thus CRT supplies u and v, and the w
condition is a single congruence. Adding positive multiples of their
common moduli makes all three at least N. After fixing u and v,
increase w further in its class until 25^w>4^u+9^v. This also makes c
arbitrarily large for fixed N.

Modulo 2^N the term 4^u vanishes, 25^w=25 and 9^v=25, so d=0.
Modulo 3^N the term 9^v vanishes, 4^u=25 and 25^w=25, so d=0.
Modulo 5^N the term 25^w vanishes, 4^u=16^(r_5)=-9, and 9^v=9.
For the last equality, 9 has order 2*5^(N-1) modulo 5^N: its order
is even by reduction modulo 5, and its square 81 has order 5^(N-1)
by (4). The three coprime moduli prove (3).

The disjoint prime supports of 4,9,25 prove primitivity and the radical
claim. The strict inequality c>a+b gives d<0, avoiding any unproved
claim about exponential Diophantine equations. Unbounded c proves the
last assertion. QED.

This is a universal proof, not a finite search. No historical novelty
is claimed for the elementary local unit-group and CRT constructions.

## 3. Scope of the finite-source failure

For fixed R=30, any schedule selecting finite uniform precision N(R)
is covered by Theorem 2, increasing it to at least 4 if necessary.
The modular zero fiber still has false ordinary additive points of
unbounded height. Any fixed nonuniform supported precision vector is
also covered by choosing N at least all its k_p.

This is stronger than a generic finite-residue ambiguity: it uses actual
discrete exponents, three fixed prime bases, exact radical 30, pairwise
coprimality, and congruence at every prime in that radical. It is weaker
than a countermodel to full global reconstruction. It does not impose
congruence at primes outside the radical, a fixed archimedean budget,
or a nonzero p-adic limit of each coordinate at its own prime.

Indeed, in any sequence from (3) with u,v,w>=N as N tends to infinity,
the 2-adic limit of a, the 3-adic limit of b and the 5-adic limit of c
are zero. Finite-level nonzero integer coordinates need not stay
nonzero in an inverse-limit completion. The nonvanishing source
contract is separate. We do not claim (7) otherwise supplies a fully
coherent adelic tower, or a genuine ABC counterexample.

The family lets c dominate a+b. It does not refute a scheme requiring
a small relative residual as well. Theorem 1 states an exact extra
inequality that excludes it. Nor does this obstruct observations at
other primes, other arithmetic information, or an independently proved
bound on source height.

## 4. An exact cost for unrestricted modular repair

Let E=Z^3 and D(a,b,c)=a+b-c. Protect every coordinate residue modulo
M, so allowed corrections are M Z^3. If d=M t, the smallest ordinary
sup norm of a correction h in M Z^3 making D((a,b,c)+h)=0 is

    cost_M(a,b,c)=M ceil(|t|/3).                         (8)

Indeed, writing h=M(k_1,k_2,k_3), the equation requires
k_1+k_2-k_3=-t. A bound |k_i|<=q implies |t|<=3q. Conversely distribute
|t| among three nonnegative integers each at most ceil(|t|/3), assigning
the signs needed to obtain -t. This attains the bound. These repairs
need not preserve positivity, primitivity or prime support.

At fixed N in Theorem 2, first fix u,v, and let w tend to infinity in
its allowed class. Then M is fixed and |d|=c-a-b is asymptotic to c.
Consequently

    log(1+cost_M(a,b,c))/log c -> 1.                     (9)

Even allowing all three coordinates to move in protected residue
classes has repair cost at the full logarithmic height scale in this
declared ordinary norm. A different comparison still needs its own
independently justified cost.

## 5. Remaining target and continuation

The positive result is the weighted-precision stopping law (1). The
negative result is an explicit fixed-radical integer family passing
every specified finite depth at all supported primes while failing
ordinary addition. It prevents substituting these congruences for the
missing conductor-to-height input.

ABC concerns only intended exact integer points, where d=0 already.
Theorem 2 neither counts nor bounds those points at fixed support. No
unrestricted ABC exponent improves here. Theorem 1 is a useful
certificate, not a proof obtained by renaming an open height hypothesis.

A continuation must add an ingredient distinguishing the fake zero
fiber: quantitative global source marking, an estimate on exact S-unit
exponent fibers, or observations outside the supported residue channels
with independently bounded cost. These are deferred, not ruled out.
Greater finite supported precision alone cannot remove this obstruction.

Evidence: complete written elementary proofs. No load-bearing computation,
external theorem leaf, or new Lean compilation.
