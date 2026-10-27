# Cross-radix transport and the actual Euler stationary obstruction

Base checkpoint: `Euler-shifted-obstruction-20261005`.
Base archive SHA256:
`7125e5ed1ce7b0a3fb25473284ac92fa1a4c6db42862980f1b07cbfb50233dea`.
The inherited files are immutable. No Lean run is made.

The target is unchanged: for every admitted ordinary
`r=(17659+2^18 T)2^640-161`, exclude a common zero of `G_r,G_r'` on
`x=10202+2^15 Z`. Radix identities below are exact. They do not close that
nonvanishing theorem.

## 1. Three operations called radix must be kept separate

For a restricted analytic function `h` on Z_2, affine argument lanes are

    L_(b,a) h(z)=h(a+bz),
    (L_(b,a) h)^(j)(z)=b^j h^(j)(a+bz).

Thus a zero's multiplicity is unchanged for every nonzero integer b. The
composition is

    L_(c,d) L_(b,a)=L_(bc,a+bd).

In particular two legal descriptions of the same affine pullback have the
same jet. On Z_2 an odd b, such as 3, is a unit: every map `z -> a+bz` is
a bijection of the entire disc. It is not a refinement into three disjoint
dyadic subdiscs. Binary lanes are contractions into parity subdiscs.

For example the rational polynomial `(z-1/5)^2` has a double zero and obeys
all these affine and mixed-radix jet identities. Consequently affine lane
compatibility alone cannot establish simplicity, even with rational data.

A radix expansion in powers of 3 is a different object: the terms `d_j 3^j`
do not tend to zero 2-adically unless the digits are eventually zero. A
ternary digit expansion therefore does not define a general dyadic limit.

Moment-variable dilation, described next, is neither of these operations.

## 2. The exact odd-radix map on the actual Euler exponent

For odd positive m put

    W_m(t)=sum_(j=0)^(m-1) (-1)^j exp((m-1-2j)t).

The finite geometric identity gives `W_m(t) cosh(t)=cosh(mt)`. Hence

    sech(t)=W_m(t) sech(mt).

Write `w_(m,k)=sum_j (-1)^j(m-1-2j)^(2k)` (including `0^0=1` at k=0).
For a restricted analytic h define

    U_m h(s)=sum_(k>=0) binom(2s,2k) w_(m,k)
                            m^(2(s-k)) h(s-k).                 (1)

Here `m^(2s)` means `(m^2)^s`, the usual restricted analytic unit power.
For k>0, `v2(w_(m,k))>=2k`. Moreover

    binom(2s,2k)=2^k P_k(s)/(2k)!,

so the summand's Gauss valuation tends to infinity at least as
`k+s_2(k)`, apart from the fixed norm of h. Integral translation does not
increase the Gauss norm. Thus (1) and its ordinary derivatives converge in
the restricted analytic algebra.

Coefficient extraction from the displayed EGF identity proves

    Ecal(N)=U_m Ecal(N) for every ordinary N>=0.

These integers are dense in Z_2, so continuity gives the exact identity
`Ecal=U_m Ecal` on Z_2. For m=3 its coefficients simplify to

    w_(3,0)=1,  w_(3,k)=2*4^k for k>0.

This is an actual map back to the original exponent, not an analogy based
on digits. It nevertheless couples h(s) to every h(s-k); an isolated
double zero does not force the image's value or derivative to vanish.

For the actual finite Euler prefix S_r and F_r=Ecal-S_r the equation is

    F_r-U_m F_r = U_m S_r-S_r.                              (2)

The nonzero right side is the mandatory finite-cutoff forcing. Under the
ordinary-moment EGF dictionary it is exactly

    W_m(t) H_r(mt)-H_r(t),
    H_r(t)=Aegf(t) f_<r(2t),
    Aegf(t)=(cosh(3t)-cosh(t))/(4t^2).

Thus this transport preserves the actual prescribed cutoff, including its
source denominator. It does not replace that cutoff by a bounded measure.

For any positive m,n the formal identity

    W_m(t)W_n(mt)=W_(mn)(t)=W_n(t)W_m(nt),
    W_m(t)=cosh(mt)/cosh(t),                               (3)

holds. For odd m,n it implies `U_m U_n=U_n U_m=U_(mn)` on restricted
analytic functions, first on integer evaluations then by density. The
forcing in (2) consequently obeys the exact cocycle

    D_(mn)=D_m+U_m D_n=D_n+U_n D_m,
    D_m=U_m S_r-S_r.

Hence composing radices 3 and 5 supplies the same equation by two routes.
There is no additional vanishing equation from this compatibility alone.

For even m, the formal EGF identity (3) remains valid. Its naive exponent
version contains `m^(2s)`, which has no continuous extension from ordinary
nonnegative s to Z_2: along `s=a+2^h -> a`, these nonzero powers tend to
zero, whereas the value at a is nonzero. Therefore one cannot import (1)
for m=2 as a dyadic analytic map by the same argument. This observation
does not exclude a separately proved, reorganized identity.

## 3. Direct triplication of the prescribed Bernoulli kernel

Put `t=z^2` and `f(t)=(z/sinh z)^2=sum beta_n t^n`. The exact hyperbolic
identity `sinh(3z)=3 sinh z+4 sinh^3 z` gives

    (3f(t)+4t)^2 f(9t)=9 f(t)^3.                         (4)

This directly targets beta, with no change from g to beta and no omitted
derivative commutator. For an ordinary r>=2 set

    p=sum_(n<r) beta_n t^n, B=sum_(q>=0) beta_(r+q)t^q,
    A=3p+4t, p9=p(9t), B9=B(9t),
    D=t^(-r)[A^2 p9-9p^3].

The numerator is divisible by t^r because `p=f mod t^r`. Expanding (4)
without deleting any cross-boundary term gives

    0 = D +(6A p9-27p^2)B +9^r A^2 B9
          +t^r[(9p9-27p)B^2+6*9^r A B B9]
          +t^(2r)[9^(r+1)B^2 B9-9B^3].                  (5)

The first exact coefficient is

    D(0)=-9(9^r-1) beta_r.                               (6)

The linear terms of (5) have constant `+9(9^r-1)beta_r`, so the new
triplication forcing cancels at the first packet as well. Every subsequent
coefficient of D remains part of (5). The cutoff degree is at most 2r-3
for r>=2; r=2 obeys the same bound.

Newton transport `T_a h=sum 8^q a_q P_q(x)h(x-q)` satisfies
`T_a T_b=T_(ab)`. Consequently (5) transports exactly to the source A(x).
Writing `G^[9]=sum 9^q gamma_q P_q A(x-q)`, its linear terms become the
corresponding `T_(6A p9-27p^2) G` and `9^r T_(A^2) G^[9]`, up to the
common nonzero normalization relating G to T_B A. These are operators on
shifted values. They are not products of values at x. The nonlinear tail
terms are also operator compositions, not powers of G(x).

## 4. A strict actual triplication-defect theorem

For every admitted index in the target chart define

    Delta_9(x)=G^[9](x)-9^161 G(x).

Then, throughout `x=10202+2^15 Z`,

    v2(Delta_9(x))=157,   v2(Delta_9'(x))=158.             (7)

This is a uniform actual-coefficient theorem. Here is the valuation proof.
The inherited exact packet bounds are

    gamma_0=2^154, v2(gamma_1)=153, v2(gamma_2)=157,
    v2(gamma_q)>=149+3q for 3<=q<161,
    v2(gamma_(161+t))=3t+s_2(t) for 1<=t<2^640,

and all normalized packets are integral. In Delta_9, q=161 disappears.
For q!=161 the new multiplier has valuation

    v2(9^q-9^161)=3+v2(q-161).

The source A(x) is a unit and `v2(A'(x))=1` for even x: its restricted
coefficients satisfy `v2([x^n]A)>=n`, and
`A'(0)=9 log(9)/8-3=2 mod 4`. Thus q=0 has exactly the valuations in (7).
Packet 1 has multiplier valuation 8, so its derivative has valuation at
least 161. Packet 2 has multiplier valuation 3, hence derivative at least
160. Packets 3 through 160 have derivative valuation at least 161.

For q>=162, use the inherited integral-argument bounds

    v2(P_q(x))>=v2(q!),
    v2(P_q'(x))>=v2(q!)-floor(log2 q).

The latter is at least 152 for q>=162 and is nondecreasing. Until
q=161+2^640, gamma has valuation at least 4 and the multiplier at least 3,
so these derivatives have valuation at least 159. Thereafter the factorial
bound alone is far stronger, and integrality of gamma suffices. Their
values are also strictly higher than 157. Hence no packet can cancel q=0.

At a hypothetical double zero of G this implies that G^[9] is nonzero
and has a nonzero derivative. It is not a contradiction: neither (5) nor
its derivative forces G^[9] or its derivative to vanish there. Retaining
all shifted operators and D is essential to this statement.

The executed discriminator separately rebuilt actual coefficients at T=0
and T=22831001499602523078606181325. At each stationary point it obtained
the value/derivative valuations 157/158, with normalized units respectively
24011/35271 modulo 65536. The calculation used 210 global bits and 180
output bits. The stationary lift has 31 Z-bits, hence 46 physical x-bits.
The inherited polynomial-jet stability bounds put the resulting value and
derivative errors above 180 bits; multiplying packets by the integral
factor `9^q-9^161` cannot weaken these bounds. Global omitted packets are
zero coefficientwise modulo 2^210. The second case's displayed zero value
of G modulo 2^180 is only a lower bound, not an exact zero.

## 5. Exact finite-state radix compilation is impossible for G_r

For each fixed ordinary r>=1 and each integer k>=2, the rational sequence
`n -> G_r(n)` has an infinite-dimensional k-kernel span over Q_2. Here the
k-kernel consists of all sequences `n -> G_r(k^e n+a)`, 0<=a<k^e.

Proof. Suppose that span has finite dimension d. Every matrix of rational
sequence evaluations has the same rank over Q and Q_2: ranks are detected
by its finite rational minors. Thus the rational k-kernel already spans a
d-dimensional Q-vector space. Choose a rational sequence basis. Digit
decimation `h(n)->h(kn+a)` is then represented by one of k rational d by d
matrices, because the kernel space is closed under this operation.

An integer n has O(log n) base-k digits. Multiplying the corresponding
matrices and evaluating at n=0 yields an archimedean bound

    |G_r(n)| <= C_r (n+1)^A_r.                            (8)

The precise exponent is immaterial; a fixed maximum of the k matrix norms
gives one. But the already proved exact interpolation identity is

    E_(2(r+n))-S_r(r+n)
       =8^r beta_r 2^mu P_r(r+n) G_r(n).                 (9)

Here P_r is a fixed polynomial, and S_r is a finite rational-exponential
function. On ordinary N>=r it is bounded in absolute value by
`C*9^N(N+1)^B`. Equations (8)-(9) would therefore bound all even Euler
numbers by another exponential times a polynomial. The even exponential
generating series `sum E_(2N)t^(2N)/(2N)!` would then be entire. It equals
sech(t) near zero, which has a pole at `t=i*pi/2`, a contradiction.

This proves the stated obstruction without assuming an Euler asymptotic
formula. It rules out an exact characteristic-zero finite-dimensional
digit-matrix representation of the full G_r value sequence. It does not
rule out finite-precision automata, an automaton for a different sequence,
a zero-set recognizer, or a nonfinite analytic radix calculus. In
particular no claim is made about automaticity of the exceptional index
set without identifying and proving a suitable finite-state model.

## 6. What survives cross-radix and cross-prime compatibility

All odd-radix identities still hold if the finite prefix is altered. More
concretely, put ell=log9 and let G be any of the actual restricted residuals.
Define

    u=-G(0), v=(-G'(0)+G(0)A'(0))/ell,
    Gtilde(x)=G(x)+u A(x)+v(9^x-1).

Then Gtilde(0)=Gtilde'(0)=0. The exact identity
`9^x-1=8P_1(x)A(x-1)` shows that this changes only the first two Newton
tail coefficients. Multiplying by the prefactor in (9) changes the source
prefix by two finite terms at indices r and r+1, while retaining all the
first r forced Euler interpolation values. With this modified finite
prefix, Ecal is unchanged and every equation (2)-(3) and its derivative
continues to hold. These modifying coefficients lie in Q_2 and need not
be the prescribed rational Bernoulli coefficients. This is a countermodel
to deriving simplicity from transport and cutoff architecture alone,
not a counterexample for the actual Euler coefficients.

A switch to another prime also requires new input. The stationary point
is an element of Z_2; rationality of r and of coefficient approximations
does not make that point rational or supply a corresponding point in Z_3.
Even common rational polynomial data can have a double zero at every
prime, as `(x-1)^2` shows. A cross-prime argument must establish an
additional global algebraic certificate with a nonzero value. Such a
certificate is not supplied by radix covariance.

## Evidence and exact remaining implication

The recovered project source
`Komorebi_Cross_Radix_Rigidity_CONTINUE_v0.12.0.zip` was read directly.
Its `BELL_EXTERNAL_INTERFACE.md` requires two-base regularity before the
external Bell route and separately supplies its finite-hull theorem with
an eventual quasi-polynomial profile interface. Section 5 proves that the
full G_r sequence fails even one-base regularity, so it cannot instantiate
that interface. This conclusion uses our self-contained argument and does
not depend on re-authenticating the external Bell result. The package's
`SCALAR_EXTENSION_BRIDGE.md` identifies the denominator-cleared shell
operator with the scaled spectral projector. Its `PROOF_BOUNDARIES.md`
explicitly leaves arithmetic membership in the shell-preservation lattices
unproved and does not claim that every arithmetic shell defect vanishes.
Those source statements do not themselves supply the missing Euler
constraint. The archive and four read entries are pinned in
`SOURCE_BOUNDARIES.json`.

`check_cross_radix.py` verifies the formal mixed-radix identities through
degree 24, 75 odd-radix Euler moment identities, the complete nonlinear
cutoff for r=2,...,9 through all available degrees, and the two actual
triplication-defect jets above. Exact rational arithmetic is used for the
formal checks. The actual check uses the inherited audited modular
Bernoulli construction. `certified_run/manifest.json` validates with all
four execution inputs pinned. The formulas and universal proofs above
have not been independently reviewed by this author.

The remaining implication is still a constraint on the prescribed
Bernoulli coefficients that excludes `G=G'=0`. The new strict theorem (7)
would help only together with a separately proved zero-propagation
relation forcing the corresponding scaled-tail jet to vanish. The actual
triplication identity (5), including its cutoff, supplies no such relation
by itself. The finite-state theorem closes a specific proposed radix
shortcut; it does not declare all radix approaches exhausted.
