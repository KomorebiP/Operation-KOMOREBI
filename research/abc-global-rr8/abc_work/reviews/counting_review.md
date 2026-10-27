# Independent audit of the global radical count

Review date: 2026-10-25. Checkpoint: ABC-20261025-RR2.

**Normalized claim and primary verdict: proved as written.** For every real
`delta>0` and positive integer `k`, with `rad(1)=1` and `omega(1)=0`,

\[
C(k,\delta)=\prod_p\left(1+\frac{k}{p(p^\delta-1)}\right)
=\sum_{n\ge1}\frac{k^{\omega(n)}}{\operatorname{rad}(n)n^\delta}<\infty.
\]

Consequently the stated weighted radical count, ordered primitive-triple
count, and fixed-positive-excess exceptional-set count all follow. These
claims do **not** prove finiteness of the exceptional set or the ABC conjecture.

## Exact claim card

- `k` is a fixed positive integer; `delta` is a fixed positive real number.
- `Z,Y>=1` are real; the sum is over positive integers `n` with `n<=Z` and
  `rad(n)<=Y`.
- `B(X,Y)` counts ordered positive triples satisfying `a+b=c<=X`,
  `gcd(a,b)=1`, and `rad(abc)<=Y`; the source assumes `X>=2,Y>=1`.
- For every fixed `epsilon,eta>0`, the exceptional-count conclusion is
  `E_epsilon(X)<=C(3,eta/3) X^[1/(1+epsilon)+eta]` for `X>=2`.
- No uniformity as `eta` tends to zero is asserted. No asymptotic or
  computation is used as a substitute for the universal proof.

## Dependency graph and independent derivation

1. **Prime-power definition.** For `e>=1`,
   `k^omega(p^e)/(rad(p^e)(p^e)^delta)=k p^(-1-e delta)`.
   Thus each local series is exactly
   `1+k/[p(p^delta-1)]`. Unique prime factorization makes the summand
   multiplicative, including its value `1` at the unit.

2. **Convergence.** For every prime `p>=2`,

   \[
   0\le\frac{k}{p(p^\delta-1)}
   =\frac{k p^{-1-\delta}}{1-p^{-\delta}}
   \le\frac{k}{1-2^{-\delta}}p^{-1-\delta}.
   \]

   The prime sum is bounded by the convergent integer sum
   `sum_(n>=2)n^(-1-delta)`. Since `log(1+x)<=x` for `x>=0`, the finite
   Euler products are uniformly bounded and have a finite limit. Expanding
   the finite products and then increasing their prime support recovers
   every positive integer exactly once. Monotone convergence of
   nonnegative terms proves the asserted identity. There is no conditional
   rearrangement.

3. **Weighted radical count.** On the indicated set,

   \[
   k^{\omega(n)}
   =\operatorname{rad}(n)n^\delta
      \frac{k^{\omega(n)}}{\operatorname{rad}(n)n^\delta}
   \le YZ^\delta
      \frac{k^{\omega(n)}}{\operatorname{rad}(n)n^\delta}.
   \]

   Summation followed by enlargement to all positive integers gives (G1).

4. **Factor allocation.** From `a+b=c` and `gcd(a,b)=1`, one obtains
   `gcd(a,c)=gcd(b,c)=1`. For fixed `n`, the ordered pairwise coprime
   factorizations `n=abc` are in bijection with assignments of each complete
   prime-power block `p^v_p(n)` to exactly one of three factors. There are
   exactly `3^omega(n)` such assignments. Units create no additional
   multiplicities. The equation `a+b=c` selects a subset. Also
   `abc<=X^3` because each factor is at most `X`. Applying (G1) with
   `k=3,Z=X^3` proves (G2).

5. **Exceptional count.** Put `s=1/(1+epsilon)`. If
   `c>rad(abc)^(1+epsilon)` and `c<=X`, then
   `rad(abc)<c^s<=X^s`. The strict condition is contained in the weak
   radical condition used by `B(X,X^s)`. Therefore (G2), with
   `delta=eta/3`, gives exactly (G3). Its explicit constant is independent
   of `epsilon`; the exponent and the choice needed for sublinearity
   depend on `epsilon`.

All leaves above are elementary internal arguments: prime factorization,
geometric series, the convergence of a positive real p-series, and the
stated definitions. No external number-theoretic theorem or computational
claim is load-bearing. There is no circular dependence on ABC.

## Obligation matrix

| Obligation | Status | Decisive reason |
| --- | --- | --- |
| Exact local Euler factor | Passed | Sum over all positive prime exponents |
| Infinite product and series interchange | Passed | Nonnegative exhaustion and finite product bound |
| `(G1)` for all real `Z,Y>=1` | Passed | Pointwise inequality before summing |
| Primitivity implies pairwise coprimality | Passed | `gcd(a,a+b)=gcd(a,b)` and its counterpart |
| Ordered multiplicity `3^omega(n)` | Passed | Bijection of maximal prime-power blocks and allocations |
| Product-height and radical cutoffs | Passed | `abc<=X^3` and unchanged full radical |
| Fixed `epsilon,eta` exceptional count | Passed | `delta=eta/3`, with explicit finite constant |
| Finiteness of exceptions / full ABC | Not addressed by the count | A growing upper count permits infinitely many heights |
| Finite verifier scope and stored output | Passed | Reproduced stated finite assertions; no universal assertion is tested |

## Boundary and quantifier checks

- At `n=1`, both sides use weight `1`, and the local-factor construction
  includes this unit. The inequality at `Z=Y=1` reads `1<=C(k,delta)`.
- At `n=1`, the unique ordered pairwise coprime factorization is `(1,1,1)`,
  agreeing with `3^0=1`; it does not satisfy the additive equation.
- The smallest primitive additive triple `(1,1,2)` is counted once; swapping
  `a,b` elsewhere is retained as an ordered pair. There is no omitted
  factor of two.
- If `Y=1`, no positive additive triple is eligible because `abc>=2`.
  The bound remains valid. If extended to `1<=X<2`, the left side is zero.
- `delta>0` is essential. The proof does not assert a finite constant at
  `delta=0`. Constants already diverge through the prime `2` local factor
  as `delta` tends to zero.
- For each `epsilon>0`, choose any fixed `0<eta<1-s`; then `E_epsilon(X)=o(X)`.
  One cannot let `eta` vary with `X` while silently keeping its constant
  fixed.

## What this establishes and what remains missing

The count is an unconditional sublinear upper bound on the number of
ordered primitive fixed-excess exceptions of height at most `X`. It also
implies that the set of their heights has natural density zero. It does
not imply either that there are infinitely many exceptions or that there
are finitely many.

For a purely logical illustration, an infinite set of heights
`{2^(2^j):j>=1}` has a counting function much smaller than every fixed
positive power of `X`. Such an abstract example is not an ABC family;
it shows why this form of upper estimate cannot force finiteness. Summing
the present estimates over dyadic height intervals gives growing,
nonsummable upper bounds and does not make the intervals eventually
empty.

The precise missing implication is an argument that excludes every
sufficiently high exceptional factor allocation satisfying `a+b=c`.
The proof retains that equation only for pairwise coprimality and the
coarse product-height bound, then discards it when counting all
allocations. The report's stated boundary is therefore accurate.

The target contract's equivalence between fixed-coefficient finiteness
for every positive exponent excess and the usual `K_epsilon` formulation
is correct as a statement about the **whole family of exponents**. A
`K_epsilon` bound at one fixed excess alone does not give coefficient-one
finiteness at that same excess; the reverse implication uses a strictly
smaller positive excess first. This subtlety does not affect (G1)--(G3).

## Source and computation checks

The source verifier was inspected and executed with `Path.write_text`
intercepted solely for its intended `results.json` output, so no original
source or result file was changed. The finite assertions reproduced:

- 109,499 ordered primitive triples with `c<=600`;
- 22 exceptions to `c^10<=rad(abc)^11` in that range;
- 500 independently enumerated ordered coprime-factor allocation cases;
- 12 exact rational local-series checks, at six listed primes and `k=1,3`.

The output list of exceptions and the four summary counts agree exactly
with the stored result. These computations are consistency checks only.
The elementary proof above establishes the universal inequalities.

## Provenance and exact revision

Independent subagent review: the initial task supplied the exact claims
without an author's desired verdict. The Euler-factor, allocation, and
exception-count implications were first reconstructed from those
definitions, before inspecting the route note and verifier. The route
note and result were then inspected for agreement. No original proof was
edited. No broad literature or novelty assessment was performed.

Audited SHA-256 values, unchanged before and after execution:

| Path under `abc_work/routes/counting/` | SHA-256 |
| --- | --- |
| `PROOF.md` | `dc83f26920f363a26b321ee249427b5c0c677b49aee02e5644c97ae84de18ed1` |
| `verify.py` | `9f4f841b60cb5d752080a37b0e5c1a29671572b6a3072e5666a46e52fe02f48e` |
| `results.json` | `37142b34183332796c266bdbf6fa7c665f06a9d437c751050ead13eb5c3da10b` |

After this audit, the root agent reexecuted the verifier through
`abc_work/reproduce.py`. The current `results.json` SHA-256 is
`f70ccc134e8ba969185f532dab6f877b6ed5d959d2646552c7a5fb94a547a613`.
The proof and verifier hashes are unchanged, and the mathematical output
fields remain the same (109,499 triples, 22 exceptions, 500 allocations,
12 local checks). The earlier result hash above records the exact output
first reviewed; the changed runtime metadata does not change the verdict.

No gap remains in the stated counting package. The cheapest useful next
mathematical check is to state a proposed additional additive saving with
its quantifiers and test whether it forces eventual emptiness, before
combining it with this count. Merely shrinking a positive power exponent
does not close the ABC obligation.
