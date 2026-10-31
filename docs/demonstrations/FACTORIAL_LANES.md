# Factorial lanes: one residue section through exact transfer

**An extended hand-worked example · Komorebi P.**

This example follows one object through residue projection, ten multiplicative factorial lanes, hypergeometric coordinates, normalization, reciprocal inversion, prime-adic valuations and refinement. Every displayed value is rational or integral. No floating-point approximation is needed.

Our fixed data are

\[
N=10,\qquad j=4,\qquad p=5.
\]

The two numerical checkpoints are

\[
\boxed{4!\prod_{r=5}^{14}(r)_{3;10}=34!}
\qquad\text{and}\qquad
\boxed{C_2=\frac{178205}{966966},\quad v_5(C_2)=1.}
\]

The first reconstructs a factorial from residue lanes. The second comes from inverting the same residue packet in factorial-normalized coordinates. The complete [exact Python program](../../examples/factorial_lanes.py) independently checks the examples and exports rational tables.

This is a companion to [Euler numbers through packets, polynomials and residuals](EULER_PACKETS.md). The Euler example starts with a reciprocal sequence. Here we start with one projected exponential section and examine the arithmetic hidden in its factorial denominators.

## A map of the calculation

| Coordinate system | Object | What becomes visible |
|---|---|---|
| Residue projection | `S_{10,4}(t)=\sum_{n\geq0}t^{10n+4}/(10n+4)!` | One of ten additive address packets |
| Step-factorial lanes | `(10n+4)!/4!=\prod_{r=5}^{14}(r)_{n;10}` | Ten disjoint multiplicative progressions |
| Pochhammer coordinates | Nine parameters plus `n!` | An exact hypergeometric expression |
| Normalized coefficients | `g_n=1/\binom{10n+4}{4}` | The denominator collapses to four factors |
| Reciprocal transfer | `G(t)C(t)=1` | A lower-triangular convolution |
| Prime-adic and refined packets | `v_5`, differences, mod-20 children | Integral control and exact reconstruction |

Two uses of the word *lane* must be kept separate. A residue projector separates **terms in a sum**. A step-factorial lane separates **factors in a product**. Their relationship is an explicit multiplicative reconstruction, not an identification of addition with multiplication.

## 1. Project the exponential onto one residue class

Begin with the familiar formal exponential,

\[
e^t=\sum_{m\geq0}\frac{t^m}{m!}.
\]

For any formal series `f(t)=\sum_{m\geq0}a_mt^m`, define the residue projector

\[
\mathcal B_{N,j}f(t)=\sum_{\substack{m\geq0\\m\equiv j\pmod N}}a_mt^m
\qquad (0\leq j<N).
\]

These operators are orthogonal and complete:

\[
\mathcal B_{N,j}\mathcal B_{N,k}
 =\delta_{jk}\mathcal B_{N,j},
\qquad
\sum_{j=0}^{N-1}\mathcal B_{N,j}=I.
\]

Our section is

\[
\begin{aligned}
S_{10,4}(t)
 &=\mathcal B_{10,4}e^t\\
 &=\frac{t^4}{4!}+\frac{t^{14}}{14!}
   +\frac{t^{24}}{24!}+\frac{t^{34}}{34!}+\cdots.
\end{aligned}
\]

An alternative coordinate description uses a primitive tenth root of unity `\zeta`:

\[
S_{10,4}(t)=\frac1{10}\sum_{\ell=0}^{9}
   \zeta^{-4\ell}e^{\zeta^\ell t}.
\]

To verify it, expand each exponential. The coefficient multiplier on `t^m/m!` is

\[
\frac1{10}\sum_{\ell=0}^9\zeta^{\ell(m-4)}
=\begin{cases}1,&m\equiv4\pmod{10},\\0,&\text{otherwise.}\end{cases}
\]

This is a coefficientwise identity over the cyclotomic field, so no analytic convergence assumption is needed.

## 2. Disassemble a factorial into ten lanes

For a positive step `N` define

\[
(a)_{n;N}=\prod_{k=0}^{n-1}(a+Nk),\qquad (a)_{0;N}=1.
\]

For our residue class,

\[
\begin{aligned}
\frac{(10n+4)!}{4!}
  &=5\cdot6\cdots(10n+4)\\
  &=\prod_{r=5}^{14}(r)_{n;10}.
\end{aligned}
\]

**Why this is exact:** every integer between `5` and `10n+4` has a unique representation `r+10k` with `5\leq r\leq14` and `0\leq k<n`. The ten lanes are disjoint and exhaust the interval.

Take `n=3`. The ten columns of the disassembly are:

| Lane `r` | Three factors `r,r+10,r+20` | Lane product |
|---:|---|---:|
| 5 | `5\cdot15\cdot25` | 1875 |
| 6 | `6\cdot16\cdot26` | 2496 |
| 7 | `7\cdot17\cdot27` | 3213 |
| 8 | `8\cdot18\cdot28` | 4032 |
| 9 | `9\cdot19\cdot29` | 4959 |
| 10 | `10\cdot20\cdot30` | 6000 |
| 11 | `11\cdot21\cdot31` | 7161 |
| 12 | `12\cdot22\cdot32` | 8448 |
| 13 | `13\cdot23\cdot33` | 9867 |
| 14 | `14\cdot24\cdot34` | 11424 |

Multiplying the ten entries, then restoring the initial `4!`, gives

\[
24\cdot1875\cdot2496\cdot3213\cdot4032
\cdot4959\cdot6000\cdot7161\cdot8448\cdot9867\cdot11424
=295232799039604140847618609643520000000=34!.
\]

There are no hidden denominators in this step.

## 3. Transport the product to hypergeometric coordinates

Write `(\alpha)_n=\alpha(\alpha+1)\cdots(\alpha+n-1)`. Every step lane obeys

\[
(r)_{n;10}=10^n\left(\frac r{10}\right)_n.
\]

Therefore

\[
(10n+4)!=4!\,10^{10n}
\prod_{r=5}^{14}\left(\frac r{10}\right)_n.
\]

Exactly one parameter is `1`, namely `r/10=10/10`. Its factor is `(1)_n=n!`. Extracting it gives the other nine parameters

\[
\mathcal A_{10,4}
=\left(
\frac12,\frac35,\frac7{10},\frac45,\frac9{10},
\frac{11}{10},\frac65,\frac{13}{10},\frac75
\right).
\]

Thus

\[
\boxed{(10n+4)!=4!\,10^{10n}n!
       \prod_{\alpha\in\mathcal A_{10,4}}(\alpha)_n.}
\]

The hypergeometric function is defined here by its coefficients,

\[
{}_0F_9\left({- \atop \mathcal A_{10,4}};z\right)
=\sum_{n\geq0}\frac{z^n}
       {n!\prod_{\alpha\in\mathcal A_{10,4}}(\alpha)_n}.
\]

Substituting the factorial identity term by term yields the exact expression

\[
\boxed{
S_{10,4}(t)=\frac{t^4}{4!}\,
{}_0F_9\left({-\atop\mathcal A_{10,4}};
                      \frac{t^{10}}{10^{10}}\right).
}
\]

This is an equality of formal power series, not an approximation by a special function.

There is a second proof using consecutive coefficient ratios. With `a_n=1/(10n+4)!`,

\[
\frac{a_{n+1}}{a_n}
 =\frac1{(10n+5)(10n+6)\cdots(10n+14)}.
\]

The hypergeometric side has the ratio

\[
\frac1{10^{10}(n+1)\prod_{\alpha\in\mathcal A_{10,4}}(n+\alpha)}.
\]

The nine parameters supply nine of the factors. `10(n+1)=10n+10` supplies the omitted `n!` lane. Both sequences start at `1/4!`, so their coefficients agree for every `n`.

**Cancellation checkpoint:** the rational parameters introduce no arithmetic loss. The common power `10^{10n}` restores the original ten integer progressions.

## 4. Remove the forced first packet

The leading term of `S_{10,4}` is `t^4/4!`. Remove it and define

\[
G(t)=\frac{4!}{t^4}S_{10,4}(t)
=\sum_{n\geq0}g_n\frac{t^{10n}}{(10n)!}.
\]

The factorial-normalized coefficients are

\[
\begin{aligned}
g_n
 &=\frac{4!(10n)!}{(10n+4)!}\\
 &=\frac{24}{(10n+1)(10n+2)(10n+3)(10n+4)}\\
 &=\frac1{\binom{10n+4}{4}}.
\end{aligned}
\]

The long denominator `(10n+4)!` has collapsed to four factors. This is the arithmetic turning point.

| `n` | Degree `10n+4` | `\binom{10n+4}{4}` | `g_n` |
|---:|---:|---:|---:|
| 0 | 4 | 1 | 1 |
| 1 | 14 | 1001 | `1/1001` |
| 2 | 24 | 10626 | `1/10626` |
| 3 | 34 | 46376 | `1/46376` |
| 4 | 44 | 135751 | `1/135751` |

This also clarifies the normalization: `g_n` is the coefficient of `t^{10n}/(10n)!`, **not** the ordinary coefficient of `t^{10n}`. Confusing those bases would remove a factor `(10n)!` from the product law below.

## 5. Invert the normalized section

Because `G(0)=1`, there is a unique formal reciprocal,

\[
C(t)=\frac1{G(t)}
=\frac{t^4/4!}{S_{10,4}(t)}
=\sum_{n\geq0}C_n\frac{t^{10n}}{(10n)!}.
\]

Now multiply `G(t)C(t)=1`. Products of exponential coefficients carry binomial weights:

\[
\sum_{k=0}^n\binom{10n}{10k}g_kC_{n-k}
=\begin{cases}1,&n=0,\\0,&n>0.\end{cases}
\]

The constant coefficient is `C_0=1`. Solving each later row gives the exact lower-triangular transfer,

\[
\boxed{C_n=-\sum_{k=1}^n\binom{10n}{10k}g_kC_{n-k}.}
\]

For `n=1`,

\[
C_1=-g_1=-\frac1{1001}.
\]

For `n=2`,

\[
\begin{aligned}
C_2&=-g_2-\binom{20}{10}g_1C_1\\
&=-\frac1{10626}+\frac{184756}{1001^2}\\
&=\boxed{\frac{178205}{966966}}.
\end{aligned}
\]

For `n=3` the same recurrence gives

\[
C_3=-\frac{163326976357}{29541512}.
\]

A finite row check is especially useful here: multiplying the computed coefficients back into `G` must give `1` and zero in every positive block degree through the chosen truncation.

## 6. See what the prime 5 detects

For every integer `n\geq0` and `r=1,2,3,4`,

\[
10n+r\equiv r\pmod5.
\]

None of the four denominator factors vanishes modulo `5`. Since `4!=24` is also a `5`-adic unit,

\[
\boxed{v_5(g_n)=0\qquad(n\geq0).}
\]

Here `v_5(a/b)` is the exponent of `5` in the numerator minus its exponent in the denominator after reduction. A rational is `5`-adically integral when this valuation is nonnegative.

In fact the chosen numbers have a stronger elementary cancellation:

\[
\binom{10n+4}{4}
=1+\frac{125}{6}\,n(1+7n+20n^2+20n^3).
\]

Because `6` is a `5`-adic unit,

\[
\binom{10n+4}{4}\equiv1\pmod{125},
\qquad
g_n\equiv1\pmod{125}.
\]

The last congruence means the denominator of `g_n` can be inverted modulo `125`. It does not mean that `g_n` is an integer in the ordinary sense.

The reciprocal recurrence uses only integral binomial weights, `5`-integral `g_k` and previous `C_{n-k}`. Induction gives

\[
\boxed{v_5(C_n)\geq0\qquad(n\geq0).}
\]

This bound is not a claim that every `C_n` is a unit:

| `n` | `C_n` | `v_5(C_n)` |
|---:|---|---:|
| 0 | `1` | 0 |
| 1 | `-1/1001` | 0 |
| 2 | `178205/966966` | 1 |
| 3 | `-163326976357/29541512` | 0 |

The extra factor of `5` in `C_2` is a real cancellation between two terms of the triangular recurrence.

## 7. Transfer the unit estimate into finite differences

Define a forward displacement on the normalized coefficient function by

\[
(\Delta_qg)(n)=g_{n+q}-g_n.
\]

For one denominator factor we have the exact identity

\[
\frac1{10(n+q)+r}-\frac1{10n+r}
=\frac{-10q}{(10n+r)(10(n+q)+r)}.
\]

All factors in the denominator remain `5`-adic units for `r=1,2,3,4`. Applying the finite product rule shows

\[
v_5(g_{n+q}-g_n)\geq1+v_5(q)
\quad (q\geq1).
\]

Repeating the argument yields the mixed-difference estimate

\[
\boxed{
v_5\bigl(\Delta_{q_1}\cdots\Delta_{q_s}g(n)\bigr)
\geq s+\sum_{\nu=1}^s v_5(q_\nu)
}
\]

for positive integer steps. At each application, a factor `10q_\nu` appears, and all shifted denominators remain units. This is a statement **about this rational function `g`**. Extending analogous bounds to other reciprocal families requires their own hypotheses.

Three checks make the estimates concrete:

\[
\begin{aligned}
\Delta_1g(0)&=\frac1{1001}-1=-\frac{1000}{1001},
&v_5&=3,\\
\Delta_5g(0)&=\frac1{316251}-1=-\frac{316250}{316251},
&v_5&=4,\\
\Delta_2^2g(0)&=g_4-2g_2+g_0
=\frac{121625}{121647},
&v_5&=3.
\end{aligned}
\]

The universal lower bounds are respectively `1`, `2` and `2`. Their measured valuations are at least as large; this example displays additional cancellation rather than assuming it.

## 8. Refine the additive packet without altering it

A degree congruent to `4` modulo `10` is congruent to either `4` or `14` modulo `20`. Consequently,

\[
\boxed{S_{10,4}(t)=S_{20,4}(t)+S_{20,14}(t).}
\]

The first child contains degrees `4,24,44,\ldots`. The second contains `14,34,54,\ldots`. There is no overlap, and neither child alone reconstructs the parent.

The ten projected exponential sections also form a closed derivative-transfer system. Set

\[
E_j(t)=\mathcal B_{10,j}e^t,\qquad j=0,\ldots,9.
\]

Differentiation moves one address backward:

\[
E_j'(t)=E_{j-1\pmod {10}}(t).
\]

For the vector `\mathbf E=(E_0,\ldots,E_9)^T` this is `\mathbf E'=P\mathbf E`, with `P` the cyclic permutation matrix and `P^{10}=I`. Hence each packet satisfies `E_j^{(10)}=E_j`. Summing all ten packets recovers `e^t`.

This derivative transfer acts on additive series packets. It must not be confused with multiplying the ten step-factorial lanes in Section 2. Both are exact decompositions of data associated with the same source, but they use different operations.

## 9. Two failure witnesses

**Remove one multiplicative lane.** If the start `r=10` is omitted from the `n=3` product, the missing factor is

\[
(10)_{3;10}=10\cdot20\cdot30=6000.
\]

The reconstructed value is `34!/6000`, not `34!`. In hypergeometric coordinates this is exactly the omitted `(1)_n=n!` factor. Omitting it without retaining the definition's `n!` changes the series.

**Move the residue across the prime boundary.** The uniform `5`-adic-unit argument above assumed `0\leq j<5`. Take `N=10` and `j=5` instead. The analogous normalized coefficient at `n=2` is

\[
\frac1{\binom{25}{5}}=\frac1{53130},
\qquad v_5=-1.
\]

Thus the unit claim does not extend unchanged to all residues `j`. The additive projection still exists. It is the particular normalization and prime-adic conclusion that fail.

## 10. General algebraic form and boundaries

For `N\geq1` and `0\leq j<N`, the same partitioning argument proves

\[
\frac{(Nn+j)!}{j!}
=\prod_{r=j+1}^{j+N}(r)_{n;N}.
\]

The interval of `N` lane starts contains `r=N` exactly once. Extracting its `(N/N)_n=n!` factor gives

\[
(Nn+j)!=j!\,N^{Nn}n!
\prod_{\substack{r=j+1\\r\neq N}}^{j+N}
\left(\frac rN\right)_n.
\]

Consequently `S_{N,j}(t)` has an exact `{}_0F_{N-1}` representation. These are purely algebraic identities.

For the normalized coefficient

\[
g_n^{(N,j)}
=\frac{j!(Nn)!}{(Nn+j)!}
=\binom{Nn+j}{j}^{-1},
\]

a sufficient condition for it to be a `p`-adic unit at every `n` is `p\mid N` and `0\leq j<p`. The factors `Nn+1,\ldots,Nn+j` are then all units. The particular case `N=10,j=4,p=5` satisfies this condition.

None of these calculations alone proves a global number-theoretic conjecture or a general Mahler-transfer theorem for an unrelated sequence. They exhibit the finite algebra and the precise hypotheses that further transfer results must respect.

## Run and audit the exact arithmetic

The standalone [factorial-lane checker](../../examples/factorial_lanes.py) uses Python 3.10 or later and only the standard library. From the repository root:

```text
python -B examples/factorial_lanes.py
python -B examples/factorial_lanes.py --output factorial-results
```

The first command reports `PASS: 225 exact finite assertions`, including the displayed lane products, hypergeometric coefficient identities, reciprocal inversion, prime-adic valuations, finite differences, refinement and failure witnesses. The second also writes `lane-products.csv`, `coefficients.csv` and `results.json`.

[Read the complete Python source on the website](https://KomorebiP.github.io/Operation-KOMOREBI/read/factorial-lanes.html) · [Download the standalone checker](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/factorial-lanes/factorial_lanes.py)

### Interpretation and next reading

The derivation is exact for all indices where the identities are stated. The program checks bounded ranges, not an infinite theorem. The general lane split is proved by unique factor addresses; the reciprocal and valuation statements are proved by formal multiplication and elementary divisibility.

Continue with the [Euler extended example](EULER_PACKETS.md), [cyclic reciprocal coefficients](../examples/16_CYCLIC_RECIPROCALS.md), [Paper IV](../works/paper-iv.md), [Special Functions](../works/monographs-special-functions.md) and the [project's evidence guide](../RECORDS.md). These links identify related mechanisms, not automatic transfer of their proof status.
