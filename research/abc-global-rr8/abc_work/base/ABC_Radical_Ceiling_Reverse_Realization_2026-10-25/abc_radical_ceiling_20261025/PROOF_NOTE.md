# ABC arithmetic continuation: two-sided radical ceilings and sparse exceptional realizations

**Research checkpoint — 25 October 2026**  
**Status:** Proven elementary inequalities, exact classification of three small multiplier families, and finite exact searches. **Not** a proof of the general abc conjecture. The counting lemma is an elementary result in the established theory of integers with bounded radical; no historical priority is claimed. Lean compilation was not undertaken.

## 1. Correct global normalization

For positive, coprime integers `a,b`, put `c=a+b`, `r(n)=rad(n)`, and `U(n)=n/r(n)`. Write `A=r(a)`, `B=r(b)`, `C=r(c)`, `u=U(a)`, `v=U(b)`. Pairwise coprimality yields

\[
 R=r(abc)=ABC,\qquad c=Au+Bv.
\]

Hence the following is a **pointwise equivalence**, without any limiting argument:

\[
 \boxed{c>R \iff C<\frac{u}{B}+\frac{v}{A}.} \tag{1}
\]

In particular `c/R<=u+v`, a weaker immediate upper bound that nevertheless shows an ABC hit requires substantial repeated-prime content on the input side. The exact inequality retains the *opposite input radical*, which is lost in the product `U(a)U(b)`.

### 1.1 The pointwise input-concentration barrier

**Proposition 1.1.** For every `0<=delta<1`, if `U(a)+U(b)<=c^delta`, then

\[
\boxed{c\le R^{1/(1-\delta)}.}\tag{1a}
\]

**Proof.** The exact identity yields `c/R<=U(a)+U(b)<=c^delta`. Therefore `R>=c^(1-delta)`, proving the statement. QED.

**Necessary condition for an actual ABC-strength exception.** If `c>R^(1+epsilon)` for some fixed `epsilon>0` and `gamma=epsilon/(1+epsilon)`, then

\[
\boxed{U(a)+U(b)>c^\gamma.}\tag{1b}
\]

Indeed, `c/R>c^gamma`. The stronger decomposed identity gives at least one of

\[
 U(a)>\tfrac12r(b)r(c)c^\gamma,\qquad U(b)>\tfrac12r(a)r(c)c^\gamma.\tag{1c}
\]

In particular the regime with both input powerful parts `c^{o(1)}` *already satisfies the full `1+epsilon` ABC bound pointwise*. Our later `H^{o(1)}` counting bound concerns weaker `c>R` **hits**, and must not be mistaken for new control of `1+epsilon` exceptions in a regime that is already pointwise settled by (1a). These results are elementary necessary conditions, not an independent estimate in the remaining high-concentration sector.

For `a=1,b=hQ` with `h` prime, `h\nmid Q`, the stronger quality violation `c>R^(1+epsilon)` is equivalent to

\[
 Q+1/h >h^\epsilon\bigl(r(Q)r(c)\bigr)^{1+\epsilon}.\tag{1d}
\]

In particular, since `r(c)>=2`, such a violation forces `Q>h^epsilon` for every `h>=2`. Hence the range `Q<=h^epsilon` is pointwise ruled out **without any averaging or primality distribution theorem**. This makes the high-input-exponent regime, rather than bounded `Q`, the nontrivial sieve target.

There can nevertheless be infinitely many ordinary `c>R` hits: for every `t>=1`, take `a=1`, `b=2^(6t)-1`, `c=2^(6t)`. Since `9|b`, `U(b)>=3`, while `r(c)=2`. Thus `c>2*r(b)=R`. This elementary family does not itself violate the full `1+epsilon` conjectural inequality for any fixed epsilon, and the input multiplier is not constrained to be prime.

## 2. Fixed offset, prime multiplier: an exact radical ceiling

**Theorem 2.1 (fixed-offset radical ceiling).** Let `a,Q,h` be positive integers such that `h` is prime, `gcd(a,Q)=1`, `h` divides neither `a` nor `Q`, and `h*r(Q)>=a`. Put `K=U(Q)`, `c=a+hQ`. Then

\[
\boxed{c>r(ahQc) \quad\Longleftrightarrow\quad r(a)r(c)\le K.} \tag{2}
\]

**Proof.** `r(ahQc)=r(a)h r(Q)r(c)` by the coprimality assumptions, and `c=a+h r(Q)K`. Thus `c>r(ahQc)` is equivalent to

\[
 r(a)r(c)<K+\frac{a}{h r(Q)}.
\]

The left side and `K` are integers and the last fraction lies in `(0,1]`, so the inequality is equivalent to `r(a)r(c)<=K`. QED.

The case `a=1` gives

\[
\boxed{1+hQ>r(hQ(1+hQ))\iff r(1+hQ)\le U(Q)} \tag{3}
\]

for all primes `h` not dividing `Q`. No restriction on the relative sizes of `h` and `Q` is required.

**Pointwise exclusion.** Since `c>1`, its radical is at least the smallest prime `p_min` not dividing `aQ`. If `U(Q)<r(a)*p_min`, every admissible sufficiently large multiplier `h` fails the ABC-hit condition. This is only a sufficient exclusion, not the general abc conjecture.

## 3. A sharper count of integers with bounded radical

Define

\[
 \mathcal N(X,Y)=\#\{1\le n\le X:r(n)\le Y\}.
\]

Let `k(Y)` be the largest nonnegative integer satisfying `(k(Y)+1)!<=Y`. The product of `k` distinct primes is at least `(k+1)!`, since the `j`th smallest prime is at least `j+1`.

**Lemma 3.1.** For `X,Y>=2`,

\[
\boxed{\mathcal N(X,Y)\le 1+\lfloor Y\rfloor(1+\log_2 X)^{k(Y)}.} \tag{4}
\]

**Proof.** If `d=r(n)`, the `k=omega(d)` distinct primes dividing `d` support at most `(1+log_2 X)^k` possible integers up to `X`, by bounding every exponent individually. There are at most `floor(Y)` eligible squarefree `d`, and `k<=k(Y)`. Include `n=1` separately. QED.

Stirling's estimate implies `k(Y)=O(log Y/loglog Y)` as `Y->infinity`.

**Theorem 3.2 (subpower radical count).** For any `Y=Y(X)>=2` with `log Y=o(log X)`, we have

\[
\boxed{\mathcal N(X,Y)=X^{o(1)}.} \tag{5}
\]

**Proof.** Put `L=log X`, `y=log Y=o(L)`. When `y<=sqrt L`, the crude `k(Y)<=y/log 2` gives `log N<=O(sqrt L(1+log L))=o(L)`. Otherwise `y>sqrt L`, so `log y>=0.5 log L`; Stirling gives `k(Y)<=C y/log y`, and then `log N<=y+O(y log L/log y)=O(y)=o(L)`. QED.

**Corollary 3.3.** Fix `A>0`. For integers `Q=Q(H)<=H^A` with `U(Q)=H^{o(1)}`, the number of primes `h<=H`, `h\nmid Q`, for which `1+hQ` is an ABC hit is **`H^{o(1)}`**. This follows from (3), with `X=1+HQ` and `Y=U(Q)`. There are only `omega(Q)=O_A(log H)` excluded prime multipliers dividing `Q`, which do not change the bound.

This is a stronger *deterministic* statement than the previous `H^{theta+o(1)}` bound when `U(Q)<=theta log H`. It counts ordinary `c>R` hits; the stronger quality-`1+epsilon` bound already follows **pointwise** in this small-input-powerful-part regime from Proposition 1.1.

For example, if `Q=q^f` with fixed prime `q`, and `h` lies in `[H/2,H]`, a quality-`1+epsilon` violation requires `q^(f-1) >= (H/2)^gamma`, with `gamma=epsilon/(1+epsilon)`. Thus the hard exponent window begins at `f >= gamma*log_q H+O_epsilon(1)`, rather than at bounded `f`.

## 4. Complete classification for Q = 4, 8, 9, 16

The prime multiplier `h` is unrestricted in size. Thus these are infinite-range classifications, not computational extrapolations.

- **`Q=4`, `K=2`:** for every odd prime `h`, the output `1+4h` is odd with radical at least 3, so no hit. For `h=2`, the triple `1+8=9` is a hit. Thus **the only prime `h` is 2**.
- **`Q=8`, `K=4`:** for odd `h`, a hit requires `1+8h=3^n`; reduction modulo 8 forces `n=2t`. Thus `h=(9^t-1)/8`. For `t=1`, `h=1` is not prime. If `t>=2` is even, the base-nine repunit has the divisor `10`. If `t>=3` is odd, it factors as `[(3^t-1)/2]*[(3^t+1)/4]`, both factors exceeding 1. The remaining `h=2` gives `17`, a non-hit. Thus **there are no prime-multiplier hits**.
- **`Q=9`, `K=3`:** with `h` odd and `h!=3`, a hit requires `1+9h=2^n`, and `2^n==1(mod 9)` forces `n=6t`. Hence `h=7*(1+64+...+64^(t-1))`. Primality forces `t=1`, giving **`h=7`, `c=64`**. Direct checks for `h=2,3` yield no further hits.
- **`Q=16`, `K=8`:** with odd `h`, a hit forces the odd `c` to be a power of `3`, `5`, or `7`, because their two-prime radical products exceed 8. Their respective orders modulo 16 are 4, 4, and 2. The candidate multipliers factor as `5*(1+81+...+81^(t-1))`, `39*(1+625+...+625^(t-1))`, and `3*(1+49+...+49^(t-1))`. The sole primes are **`h=5` producing `c=81`** and **`h=3` producing `c=49`**. The special case `h=2` is not a hit.

Each proof uses elementary congruences and factorizations. There is no need for any analytic number theory input.

## 5. Reverse enumeration of genuine prime-multiplier ABC hits

For fixed `Q` and a bound `H`, the exact criterion (3) suggests enumerating candidate **outputs** `c` with `r(c)<=K` and `c<=1+HQ`, rather than scanning all primes `h<=H` or factoring each `1+hQ`.

For each candidate `c`, check `c==1(mod Q)`, set `h=(c-1)/Q`, and test primality and `h\nmid Q`. This exhaustively finds every hit in that range.

For `Q=243=3^5` and `K=81`, the provided exact implementation gives:

| Prime-multiplier bound `H` | Candidate outputs with `rad(c)<=81` | Candidate multipliers coprime to `Q` | ABC-hit prime multipliers |
|---:|---:|---:|---|
| `10^6` | 4,417 | 6 | `5, 241, 643` |
| `10^9` | 10,556 | 12 | `5, 241, 643` |

The corresponding exact primitive triples are

\[
 1+243\cdot5=1216=2^6\cdot19,
\]
\[
 1+243\cdot241=58564=4\cdot11^4,
\]
\[
 1+243\cdot643=156250=2\cdot5^7.
\]

The table is an **exhaustive finite computation up to the stated `H`**, not a proof that no larger prime multiplier will give a hit.

## 6. Why this does not finish abc

The new bound only controls the number of hit triples when the **input powerful part** is subpolynomial in the search height. ABC is a pointwise inequality and also includes input factors with powerful part comparable to a positive power of their heights.

Moreover, the reverse enumeration becomes much more expensive when `K` is large. If `K` grows like `H^delta`, the allowed output radical can be large enough for the count to cease being subpower. An isolated exceptional `c` may still have extreme quality without violating any counting theorem.

**Remaining research target:** a pointwise height inequality for primitive triples whose input powerful parts are polynomially large, relative to the opposite radical and output radical as in (1c). The present result stratifies the obstruction and gives a reverse-enumeration algorithm for the small-powerful-part regime. Neither statement advances the unrestricted high-concentration height inequality by itself.

## 7. Verification boundary

The accompanying `verify.py` uses only the Python standard library and records `RESULTS.json`. It checks 54,795 primitive triples for the exact two-sided identity, 70,164 fixed-offset specializations, and the six reverse enumerations listed in the results. The primality test uses the deterministic 64-bit Miller–Rabin basis set, and all enumerated multipliers lie in that range.

The finite checks substantiate the implementation, not the universal mathematical proofs. No Lean kernel verification was performed for this checkpoint. Claims of historical originality are not made.
