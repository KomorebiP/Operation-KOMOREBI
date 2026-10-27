# Height and nonintersection attempt

## Outcome

No bound `v2(Phi_r(0))<2r-25` was proved. The exact epsilon theorem supplies
a useful necessary-and-sufficient reduction, but the ordinary rationality of
the Bernoulli packet scalars does not put the critical value in a number field.
The most direct rational-height and logarithmic-form routes therefore stop
at specific missing hypotheses, identified below. No additional parameter
digits were computed in this attempt.

## Exact sufficient theorem and exact obstruction

For a fixed certified terminal-161 deep quadratic chart, let

    a_r=Phi_r(0),  E_r=2r-25,

and let eta_r^* be the unique singular parameter in the independent epsilon
family. The proved isometry gives

    v2(eta_r^*)=v2(a_r),
    v2(Phi_r(2^E_r))=v2(2^E_r-eta_r^*).

Thus any one of the following is sufficient for simplicity of this chart:

* a_r=0;
* v2(a_r) != E_r;
* v2(a_r)=E_r but 2^-E_r eta_r^* !=1.

A strict upper bound below E_r is sufficient but stronger than necessary.
The exact missing assertion is that eta_r^* is not the specified power of two.

## Why quadratic preparation does not supply a height

The prepared quadratic lies in Z_2[Z], not in Q[Z] or in a proved fixed number
field. Its coefficients are limits of all-precision preparations of infinite
analytic packet sums. The degree two bounds root multiplicity and local root
count, not arithmetic height. Likewise the unique critical point belongs to
Z_2; no polynomial over Q defining it has been constructed.

This distinction cannot be omitted. Already the family

    f_M(Z)=Z^2+2^M,   M>=1,

has fixed degree, unit quadratic coefficient, zero higher coefficients, and
critical value of valuation M. Every such polynomial satisfies the same
quadratic-class conditions used in the epsilon argument. For any fixed
coefficient precision N, all M>=N are indistinguishable from Z^2 at that
precision, although their critical values have arbitrarily large finite
valuations. This does not model the actual Bernoulli coefficients. It proves
that an upper bound must use a genuinely additional arithmetic property of
those coefficients, not preparation degree or unit transversality alone.

## Exact rational specialization and why it does not reach the critical point

Let U,V be the source-elimination sums built from the actual rational scalars:

    U(x)=gamma_0+D(x) sum_(q>=1) 9^-q gamma_q P_(q-1)(x),
    V(x)=gamma_0+D(x) sum_(q>=1) gamma_q P_(q-1)(x),
    D(x)=(x+1)(2x+1).

The same construction and every termination assertion below hold for the
depleted scalars, which are also rational at a fixed ordinary integer r.
Use those hatted versions when applying the discussion to a_r=Phi_r(0).

For an ordinary integer m>=0, `P_(q-1)(m)=0` for q>=m+2. Hence U(m),V(m)
are finite rational sums, and

    8D(m)G(m)=9^(m+1)U(m)-V(m)

is rational. This is the exact place where Bernoulli rationality is useful.

At a general dyadic critical argument, the same sums do not terminate.
Even if that argument were assumed algebraic, an infinite convergent series
with rational coefficients need not have an algebraic value. At an ordinary
integer m, differentiation also destroys termination: for q>=m+2, the single
factor x-m in P_(q-1) gives a generally nonzero derivative at m. Thus finite
rational values at nonnegative integers do not turn the critical equation
into a finite algebraic equation.

Consequently neither U(c), V(c), their derivatives, nor c itself has the
bounded-degree/height certificate needed by an elementary Liouville bound.
No assertion that these quantities are transcendental is needed here; their
algebraicity simply has not been established.

## Rational approximation does not repair the height gap

For a nonzero rational a/b in lowest terms, the elementary estimate is

    v2(a/b)<=log2(max(|a|,|b|)).

To transfer it to an analytic target z via an approximation q_P, one needs

    v2(z-q_P)>=P,
    0!=q_P,
    log2 H(q_P)<P.                                            (1)

Then v2(z)=v2(q_P)<P. A finite modular representative has height below 2^P
only when its residue is nonzero, so using that representative merely
rephrases the finite nonvanishing check; a zero residue gives no estimate.

An ordinary integer representative of the critical argument creates a more
severe problem in source elimination. Write c_N in [0,2^N) for its Z-coordinate
residue and m_N=10202+2^15 c_N. Exact source values contain

    9^(m_N+1).

Its binary logarithmic height is exactly (m_N+1) log2 9. The available bound
on m_N is exponential in N, while ordinary analytic approximation gives only
linear precision in N. Stationarity improves value precision from N to2N,
which still does not produce (1). This does not rule out a special cancellation
or a special low-height approximation theorem, but neither has been proved.

The power-series alternative has the same logical issue. For

    L_M=sum_(h=1)^M (-1)^(h+1)8^h/h,

the error in approximating log9 has valuation at least

    3(M+1)-floor(log2(M+1)).

Writing L=lcm(1,...,M), the elementary rational height bound obtained by
clearing denominators is at most

    log2 L+log2 M+3M.

For M>=2, this available upper bound is at least the certified precision scale
and does not give the strict inequality (1). Further cancellation information
would again be required. This is a failure of this particular estimate,
not a proof that every possible height strategy must fail.

## Primary-source check for p-adic logarithmic forms

Source checked on 2026-10-05:

Kunrui Yu, *Linear forms in p-adic logarithms III*, Compositio Mathematica
91 (1994), 241-276. Stable primary PDF:
https://www.numdam.org/article/CM_1994__91_3_241_0.pdf

The introduction on printed p.241 specifies nonzero algebraic bases in a
number field and ordinary integer exponents. It estimates the valuation
of a nonzero product of those powers minus1. Printed pp.242-244 continue
the number-field setup and explicit main-theorem hypotheses. The paper
treats primes including2; an odd-prime-only theorem is not being imported.

Application audit to our exact expression

    9^(x+1) U_0(x)/V_0(x)-1:

| Required source datum | Project status |
| --- | --- |
| Nonzero algebraic bases in a number field | 9 is rational; U_0(c)/V_0(c) has no established algebraicity |
| Ordinary integer exponents | c+1 is only known to lie in Z_2 |
| Controlled number-field degree and heights | Not supplied |
| Nonzero expression | May be handled by separating the exact-zero case, but does not repair the other failures |

More general logarithmic-form theorems with algebraic coefficients would
still require algebraicity and height information about c and the evaluated
unit ratio. Those are not supplied by the current Euler analysis. No Yu
estimate is invoked in the proof, and no numerical constant is claimed.

Search scope: direct primary paper and its published bibliographic record,
plus discovery queries for p-adic logarithmic forms with algebraic bases.
This is a hypothesis applicability check, not a novelty search or an audit
of every transcendence theorem. No odd-p Euler interpolation was used.

## What would make this route productive

A valid next input would be one of the following genuinely stronger theorems:

1. An exact finite algebraic description of the critical obstruction with
   an arithmetic height bound depending on r and sufficient relative error.
2. A proved transcendence/Diophantine approximation estimate directly for
   the specific Bernoulli-source analytic value at its critical point.
3. A direct unit identity showing v2(a_r) !=2r-25, or showing the normalized
   leading unit of eta_r^* is not1 when those valuations coincide.

The epsilon theorem and normalized source equations accurately isolate
these requirements. This attempt does not supply any of them, and therefore
does not close actual Euler nonintersection.
