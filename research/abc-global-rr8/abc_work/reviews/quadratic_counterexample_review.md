# Independent review of the full-radical and nonescape routes

Review date: 2026-10-25. Checkpoint: ABC-20261025-RR2.

**Primary verdict: correct only after a stated restriction.** The new
theorems and explicit families in both route notes are proved under their
displayed hypotheses. The restriction concerns Route C's blanket
endorsement of the inherited fixed-offset normalization: that inherited
statement is valid only when `gcd(h,Q)=1` is retained explicitly. Read as
a stand-alone statement, inherited Section 6 omits this hypothesis and
has a counterexample. This does not affect the inherited `a=1` main
theorems or the new route results, which impose the needed coprimality.

Neither route proves ABC or produces fixed-positive-excess counterexamples.

## Claim cards and dependencies

The full-radical route uses positive integers, `r(n)=rad(n)` and
`U(n)=n/r(n)`, with both functions equal to `1` at `n=1`. Its restricted
family has squarefree `h`, `gcd(h,Q)=1`, `c=1+hQ`, real `H>=2` with
`H/2<h<=H`, and fixed `epsilon>0`. The counting results additionally
use a fixed finite nonempty prime set `S`, fixed `A>epsilon`, and either
fixed `delta>0` or fixed `0<t<1`.

The nonescape route concerns the primitive triples `(1,hQ,1+hQ)`.
Its first family permits arbitrary positive integer multipliers coprime
to `Q`; its second has a prime multiplier `p>=5` and varying `Q`.
Indices `k,t` in these families are nonnegative **integers**, as the note
states. An ordinary hit means `c>rad(abc)`, with no fixed positive
excess in the exponent.

The dependency graph is:

1. prime factorization and local geometric series -> full-radical
   Dirichlet sum -> (A) -> radical ceiling -> (B) -> (C);
2. nonnegative divisor expansion of `U(n)^t` -> convergent Euler factors
   -> moment bound (D) -> Markov bound (E) -> smooth geometric sum (F)
   -> (G), including explicit exponent (H);
3. prime factorization of `u^k-1` -> perfect-power cutoff (I);
4. explicit modular arithmetic -> fixed-`Q` family -> constant output
   radical and ordinary-hit inequality;
5. binomial valuations -> varying-`Q` family -> sufficient ordinary-hit
   criterion, with odd exponent preserving its nonsquare output kernel.

No load-bearing external theorem or finite computation is needed.

## Full-radical route: independent derivation

### Counting and the dyadic family

For `delta>0`, the local series is

\[
1+\sum_{e\ge1}p^{-1-e\delta}
=1+\frac1{p(p^\delta-1)}.
\]

Its excess has a summable `O_delta(p^(-1-delta))` bound. Nonnegative
finite-prime exhaustion proves the Euler identity and its finite value
`C_delta`. On the set `n<=X,r(n)<=T`, the pointwise inequality
`1<=T X^delta/[r(n)n^delta]` then proves (A). The unit case and real
cutoffs `X,T>=1` cause no boundary issue.

Coprimality of `h,Q,c`, and squarefreeness of `h`, give exactly
`R=h r(Q)r(c)`. An exception yields

\[
r(c)<\frac{c^{1/(1+\epsilon)}}{h r(Q)}
<\frac{2(1+HQ)^{1/(1+\epsilon)}}{H r(Q)}.
\]

The map `h->c` is injective, so (A) with `X=1+HQ` gives (B), including
its factor `2`. If the displayed radical ceiling is below `1`, the
exception set is empty; this is the trivial empty-set case before
applying (A), whose printed domain assumes `T>=1`.

For `Q<=H^A`, put `s=1/(1+epsilon)` and
`delta=eta/(1+A)`. Since `1+HQ<=2H^(1+A)` and `r(Q)>=1`, each term in
(B) is at most a fixed constant times

\[
H^{(1+A)(s+\delta)-1}
=H^{(A-\epsilon)/(1+\epsilon)+\eta}.
\]

The number of `S`-smooth `Q` is bounded by the product over `p in S` of
`1+A log(H)/log(p)`, proving (C). This counts pairs and hence bounds the
number of distinct multipliers. It is not a pointwise bound for each
multiplier. Dependence on `S,A,epsilon,eta` is permitted as stated.

### The endpoint `Q<=H^epsilon`

Here `H<2h` gives the strict inequality `Q<(2h)^epsilon`. Also
`r(c)>=2` and `R>=2h`. Thus

\[
c=1+hQ<1+h(2h)^\epsilon
\le2h(2h)^\epsilon=(2h)^{1+\epsilon}\le R^{1+\epsilon}.
\]

The middle inequality follows from `h(2h)^epsilon>=1`. Therefore the
claimed exclusion includes the endpoint `Q=H^epsilon`; the strictness
comes from `h>H/2`, not from a missing strict bound on `Q`. This argument
does not use a fixed prime alphabet. The statements with `A>epsilon`
are compatible with the empty range `A<=epsilon`.

### Moment refinement and exponents

The multiplicative coefficients satisfy

\[
b_t(p)=0,\qquad
b_t(p^e)=p^{t(e-1)}-p^{t(e-2)}\quad(e\ge2).
\]

They are nonnegative for `t>0` and telescope to
`sum_(d|n)b_t(d)=U(n)^t`, including `n=1`. For `0<t<1`,

\[
\sum_{e\ge2}\frac{b_t(p^e)}{p^e}
=\frac{(p^t-1)p^{-2}}{1-p^{t-1}}.
\]

The local excess is `O_t(p^(t-2))`, whose sum converges. Interchanging
nonnegative sums and using `floor(X/d)<=X/d` proves exactly
`sum_(n<=X)U(n)^t<=D_t X`, which is (D).

The exception inequality is equivalent, not just sufficient, to
`U(c)>h r(Q)c^gamma`, where `gamma=epsilon/(1+epsilon)`. Since
`h>H/2` and `c>HQ/2`, applying (D) at `X=2HQ` gives

\[
N_Q\le
\frac{2D_tHQ}{[(H/2)r(Q)(HQ/2)^\gamma]^t}
=2^{1+t(1+\gamma)}D_t
 H^{1-t(1+\gamma)}\frac{Q^{1-\gamma t}}{r(Q)^t}.
\]

Thus (E), including its constant and all exponents, is correct. Its
threshold is strictly positive, so no missing small-threshold case occurs.

For (F), after fixing the exponents outside one selected prime `p_1`,
write their product as `L`. The sum
`sum_(e:p_1^e<=Y/L)(L p_1^e)^b` is at most
`p_1^b/(p_1^b-1) Y^b`. There are
`O_S((1+log Y)^(|S|-1))` possible remaining exponent vectors.
This proves (F) for `Y>=1,b>0`, including `|S|=1` and `Q=1`.
Since `1-gamma t>0`, inserting (F) into (E) proves the exact exponent

\[
1+A-t[1+\gamma(1+A)]
\]

in (G). Its limit at `t=1` is `(A-epsilon)/(1+epsilon)`.
For `epsilon=1/10,A=1/2,t=99/100`,
`gamma=1/11` and the bracketed product is `9/8`, leaving `3/8` exactly.

The constant is allowed to grow as `t` tends to `1`. Neither substituting
`t=1` in (D) nor treating this constant as uniform is authorized. The
finite verifier checks telescoping at `t=1` solely as an algebraic
identity; its docstring correctly disclaims convergence at that endpoint.

### Higher powers

For prime `h`, `gcd(h,Q)=1`, and `u^k-1=hQ`, put
`A=u-1`, `B=1+u+...+u^(k-1)`. Then `AB=hQ` and
`gcd(A,B)|k`. If `h` divided both, one would have `h<=k`, and
`k<=((Q+1)^k-1)/Q` by binomial expansion. In fact this branch is
impossible under `gcd(h,Q)=1`, because `v_h(hQ)=1`; its inclusion does
not invalidate the upper bound. If `h` divides exactly one factor, the
other divides `Q`. Either `A<=Q` directly or `B<=Q` with `A<=B` gives
`u<=Q+1`. Hence (I) follows. At `k=2`, its right side is `Q+2`.

For the canonical decomposition `c=m u^k`, each exponent in the
`k`th-powerfree `m` is at most `k-1`. Thus
`m<=r(c)^(k-1)`, and equality is possible when all relevant residues
are `k-1`. The warning about the larger discarded coefficient is accurate.

## Nonescape route: independent derivation

### Fixed `Q=243`, without a prime/squarefree multiplier requirement

The finite modular constant `5^486=1 mod 729` holds exactly. Consequently,
for integer `k>=0`, `u_k=5^(3+486k)` satisfies `u_k=125 mod 243` and
`10u_k^2-1=243*643 mod 729`, because
`10*5^6-1=243*643`. Hence

\[
h_k=(10u_k^2-1)/243\in\mathbb Z_{>0},\qquad h_k=1\pmod3.
\]

Thus `gcd(h_k,243)=1`. Substituting
`u_k=125+243t_k` gives exactly
`h_k=2430t_k^2+2500t_k+643`; `t_k` is a nonnegative integer. The
polynomial discriminant is `40`, a nonsquare, proving irreducibility
over the rationals in this branch.

Since `c_k=2*5^(7+972k)`, both its radical and squarefree kernel are
exactly `10`. Also `gcd(h_k,c_k)=1`, so

\[
\operatorname{rad}(h_k\,243\,c_k)=30\operatorname{rad}(h_k)
\le30h_k<243h_k+1=c_k.
\]

The triples `(1,243h_k,c_k)` are primitive positive ordinary hits and
their heights tend strictly to infinity. The sequence imposes no
primality or squarefreeness on `h_k`. It therefore disproves radical
escape based solely on congruence, this irreducible progression, and
multiplier coprimality; it does not disprove a lemma that additionally
uses infinitely many prime or squarefree multipliers. The note retains
this distinction.

### Prime multipliers and varying `Q`

Let `p>=5` be prime, `B=p+1`, and `q` any prime dividing `B^2+B+1`.
The latter integer is odd, so `q` is odd; it equals `3 mod p`, so
`q!=p`. Therefore `p` does not divide the integer `n_t=3q^t`.
The expansion modulo `p^2` gives

\[
(1+p)^{n_t}-1=n_tp\pmod{p^2},
\]

so `Q_t=(B^{n_t}-1)/p` is positive integral and `gcd(p,Q_t)=1`.
Also `gcd(B,Q_t)=1`.

For odd `q`, if `v_q(x-1)=s>=1`, the binomial term `q(x-1)` has
valuation `s+1`; every other term has valuation at least `s+2`.
Thus `v_q(x^q-1)=s+1`. Apply this successively beginning with `x=B^3`.
Since `q|B^3-1` and `q!=p`, this proves the exact identity

\[
v_q(Q_t)=v_q(B^3-1)+t\ge t+1,
\]

including `t=0`. In particular `U(Q_t)>=q^t`. With `R_B=r(B)`,
pairwise coprimality gives

\[
\operatorname{rad}(pQ_tc_t)
=p\operatorname{rad}(Q_t)R_B
\le\frac{pQ_tR_B}{q^t}
\le pQ_t=c_t-1<c_t
\]

whenever `q^t>=R_B`. Equality at the threshold presents no gap.
There are infinitely many such integer `t`, and their `Q_t` increase
without bound. Since `n_t` is odd, multiplication by `n_t` preserves
all prime-exponent parities in `B`; the squarefree kernel of `c_t` is
therefore that of `B`. It exceeds `1`: if `B=s^2`, then
`p=(s-1)(s+1)`, impossible for a prime `p>=5`. The exclusion of `p=3`
is necessary for this nonsquare conclusion.

Thus arbitrarily large prime multipliers admit ordinary hits when `Q`
is unrestricted. The family does not stay in a fixed polynomial bound
`Q<=H^A` with `H` comparable to a fixed multiplier `p`, and its `Q`
prime alphabet is not fixed by the argument. It does not contradict the
restricted growing-`Q` exception counts.

The certified ratio obeys
`c_t/rad(pQ_tc_t)>q^t/R_B`. This gives quality greater than `1` but
does not give a fixed positive excess: the logarithm of the certified
gain grows only on the order of `t`, while
`log(c_t)=3q^t log(B)`. No lower bound on `rad(Q_t)` is established,
so even a claim that the **actual** qualities tend to `1` would be
unjustified. The note makes no such claim.

## Inherited fixed-offset qualification

The inherited note's Section 6 prints these local assumptions:
`a>=1`, `gcd(a,Q)=1`, squarefree `h`, and `gcd(a,hQ)=1`.
These do not by themselves imply `gcd(h,Q)=1`. Read with only those
local assumptions, its displayed normalization is false.

The exact counterexample is `a=1,h=2,Q=4,c=9`. It satisfies every
locally printed assumption and
`c=9>rad(a h Q c)=6`. However `K=U(Q)=2`, `A_0=U(a)=1`, and

\[
\operatorname{rad}(c)=3\not<
K/\operatorname{rad}(a)+A_0/[h\operatorname{rad}(Q)]
=2+1/4.
\]

If Section 1's `gcd(h,Q)=1` is intended as a persistent ambient
assumption, the normalization is correct. To make the fixed-offset
statement usable independently, this hypothesis must be explicit. With
it, all of `a,h,Q,c` have the pairwise coprimality needed to write
`rad(a h Q c)=rad(a) h rad(Q)rad(c)` and divide as claimed. The root
coset and counting argument then follow.

The inherited verifier imposes `gcd(h,a*Q)=1` in both its hit enumerator
and its root counter, so it checks the restricted reading and cannot
detect the missing stand-alone hypothesis. Its reported instance-count
limitation is also confirmed: `prime_multiplier_instances`,
`quality_instances`, and `offset_instances` sum interval bounds `H`
rather than counted tested multipliers. The inherited `a=1` statements,
root counts, quality ceiling, discriminant, and prime perfect-square
cutoff reconstruct correctly under their explicitly stated hypotheses.

Route C Section 3's inherited endorsement must therefore be understood
with this retained coprimality hypothesis; it should not endorse the
fixed-offset statement under only its locally displayed assumptions.
No inherited or new proof file was edited for this review.

The subsequently supplied `abc_work/ERRATA.md` now states the complete
sufficient hypotheses and the corrected standalone normalization. Its
derivation agrees with this audit. The archived source remains unchanged,
so this is an explicit correction alongside the historical statement.

## Obligation matrix

| Obligation | Status | Scope |
| --- | --- | --- |
| Full-radical product and count (A) | Passed | Every fixed `delta>0` |
| Restricted-family ceiling and bounds (B),(C) | Passed | Squarefree `h`, `gcd(h,Q)=1`, fixed parameters |
| Endpoint exclusion | Passed | Includes `Q=H^epsilon` |
| Moment identity and convergence (D) | Passed | `0<t<1`; unit included |
| Moment threshold and powers (E)--(H) | Passed | Explicit exponent `3/8` exact |
| Smooth sum (F) | Passed | Nonempty `S`, `b>0`, `Y>=1` |
| Higher-power cutoff (I) | Passed | Prime `h`, `k>=2`, `u>=2` |
| Fixed-`Q` family's congruence and radical | Passed | Integer multipliers; no prime/squarefree assertion |
| Varying-`Q` valuations and hit endpoint | Passed | Every prime `p>=5`, integer `t>=0` |
| Irreducible output kernel | Passed | Odd exponent; excludes `p=3` |
| Inherited fixed-offset normalization | Failed under stand-alone local hypotheses | Requires explicit `gcd(h,Q)=1`; counterexample above |
| Finite verifier contracts | Passed | Listed finite parameters only |
| Full ABC / fixed-positive-excess violations | Not addressed by these results | Pointwise height or radical information remains missing |

## Finite checks and exact provenance

Both delivered verifiers were inspected and executed with their
`Path.write_text` calls intercepted at the intended result-file output.
Original proofs, code, and result files remained unchanged. The stored
mathematical output fields reproduced exactly:

- Quadratic route: 3,000 telescoping identities; 23,785 quality/threshold
  pairs containing 3 `epsilon=1/10` exceptions; 182 perfect-power
  witnesses in the explicitly bounded search; exact exponent `3/8`.
- Nonescape route: 5 fixed-`Q` examples and 17 varying-`Q` examples.
  The latter verifier correctly skips `p=29,q=7,t=1` because `7<30`;
  its comment suggesting both tested `t` values always qualify is
  inaccurate but does not affect any assertion or output.
- The fixed-`Q` modular constant, initial identity, and discriminant
  were additionally evaluated directly with exact integer arithmetic.

The nonescape verifier deliberately avoids factoring huge `Q_t` and
does not test primality or squarefreeness of the fixed-`Q` multipliers.
Its proved prime-power divisor bound suffices for its stated ordinary-hit
checks. None of these finite ranges is evidence for an unbounded ABC
claim, and none is used in the universal derivations above.

The review was performed independently of the route authors, from the
raw displayed definitions and derivations. A further fresh subagent
received only the exact varying-`Q` formulas and independently checked
the valuations, strict endpoint, output kernel, and quality limitation.
Agreement is auxiliary; the explicit derivations are the evidence.
No literature or historical-originality claim was audited.

SHA-256 values of the exact audited revisions:

| Path under `abc_work/` | SHA-256 |
| --- | --- |
| `routes/quadratic/PROOF.md` | `398c87222009ce1790f8c2878bba4ea2808ba6afd0adb0de1346b43e5d04b51a` |
| `routes/quadratic/verify.py` | `9246e5e6d0f2f478e591bc8de318bd1ce25bc6442b888d0f7756e3aaf02aa1d1` |
| `routes/quadratic/verification.json` | `bfdf9f5ac38cc6e1c557e4d571d444ec7b9b4b785b6d531737f394741a1622ae` |
| `routes/counterexample/PROOF.md` | `74f00059169bbf269036bfdf4b46d8b6a16836f1776eb46a7a2490537cf92999` |
| `routes/counterexample/verify.py` | `4408c11fc189bef474aff14f3fd172e6dee56eef19403857bdc390865966e544` |
| `routes/counterexample/results.json` | `50d7c36f423352ce6b15ad0c9063cf95c8e8ffe1dbbb71ed73716d0f2751e9d1` |
| `base/ABC_Square_Kernel_Reverse_Realization_2026-10-25/abc_square_kernel_bridge_20261025/PROOF_NOTE.md` | `8327e169e70cedfd7576187cd0c6b2e2a46211916241540761b6c3b517484b27` |
| `base/ABC_Square_Kernel_Reverse_Realization_2026-10-25/abc_square_kernel_bridge_20261025/verify.py` | `c42a444d512f06a23f9661e65182d9b7beef3cef881b26fa34fb30cbb9ce5470` |
| `ERRATA.md` | `c990d3502c9496e687532ea1e67656d4cc3d8fc6fada14901849a5c30ce13b15` |

## Remaining mathematical obligation

The strongest safe positive statements are the displayed restricted
exception counts, the prime perfect-power cutoff, and the two ordinary-hit
families with their precise multiplier domains. A growing power upper
bound permits infinitely many exceptional heights, and ordinary-hit
families do not yield a fixed positive exponent excess.

The next useful mathematical check is a fully quantified estimate that
uses both the additive/congruence realization and the full output radical
to force eventual emptiness at each fixed positive excess. No such
estimate has been supplied in these routes. The cheapest editorial
correction is to state the retained `gcd(h,Q)=1` assumption explicitly
in any independently quoted inherited fixed-offset theorem.
