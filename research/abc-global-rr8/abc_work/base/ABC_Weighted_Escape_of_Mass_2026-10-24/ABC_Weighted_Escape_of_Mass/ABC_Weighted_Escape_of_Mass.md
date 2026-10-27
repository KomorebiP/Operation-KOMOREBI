# ABC: quadratic-order averaging and escape of weighted prime-power mass

**Research continuation, 24 October 2026**  
**Status:** Three unconditional elementary estimates, one application of established p-adic logarithmic-form theory, exact computational checks, and an explicit open frontier. This does **not** prove ABC. The results have not been checked in Lean. No claim of historical priority is made.

## 1. Normalization and what must be bounded

For a primitive positive triple `a+b=c`, write

\[
D=\operatorname{rad}(ab),\quad R=\operatorname{rad}(abc),\quad
M=c/\operatorname{rad}(c),\quad \frac{c}{R}=\frac MD.
\]

The weighted powerful-part identity is
\[
\log M=\sum_{p\mid c}(v_p(c)-1)\log p.
\]

In the fixed-base family `U_f=1+h q^f`, an output prime can be ordinary (non-Wieferich to base `q`) or exceptional, and can be fixed as `f` varies or move with the height. Previous work established exact local densities and a tail bound `O_q(Y^{-1/3})` for the ordinary channels. The first new theorem improves this rate by retaining an exact multiplicative-order weight that was lost in the earlier estimate.

## 2. Improved order-summability with exponent one half

**Theorem A.** Let `q>=2` be a fixed integer, `d_p=ord_p(q)` for odd primes `p` not dividing `q`. For all `Y>=3`,

\[
\boxed{\sum_{p>Y,\ p\nmid q}\frac{\log p}{(p-1)d_p}\ll_q Y^{-1/2}.}
\]

**Proof.** On a dyadic interval `x<=p<2x`, choose `D_0=floor(sqrt(x))`. For each exact order `1<=d<=D_0`, the product of the *distinct* primes in the interval with order `d` divides `q^d-1`. Therefore

\[
\sum_{x\le p<2x,\ d_p=d}\log p\le\log(q^d-1)\le d\log q.
\]

The corresponding contribution to the weighted sum is at most `log(q)/(x-1)` *per order d*. Hence the total over small orders is at most `D_0 log(q)/(x-1)=O_q(x^{-1/2})`.

For `d_p>D_0`, use `1/d_p<=1/D_0` and the Chebyshev bound `sum_{x<=p<2x} log(p)/(p-1)=O(1)`. The large-order contribution is also `O(x^{-1/2})`. Sum over intervals `[2^jY,2^{j+1}Y)` to obtain the tail `O_q(Y^{-1/2})`. QED.

*Comparison with the predecessor.* The preceding proof bounded the number of small-order primes after grouping all orders, losing a factor `1/d`. Keeping the group-by-order product gives the sharper square-root rate. This is an elementary bound, not a global ABC inequality.

## 3. Moving-height control for all ordinary repeated layers under a prime-power cutoff

Let `h>=1` be any integer, `F>=1`, `Y>=3`, `X>=4`. Let `p` run over odd primes with `p∤hq` and `v_p(q^{d_p}-1)=1`. Define the truncated weighted contact

\[
\mathcal E_{Y,X}(f)=
\sum_{\substack{p>Y,\ p\nmid hq\\v_p(q^{d_p}-1)=1}}
\sum_{\substack{e\ge2\\p^e\le X}}
(\log p)\,\mathbf1_{p^e\mid(1+hq^f)}.
\]

**Theorem B.** Uniformly in `h`, `F`, `Y` and `X`,

\[
\boxed{\frac1F\sum_{f=1}^F\mathcal E_{Y,X}(f)
\ll_q Y^{-1/2}+\frac{\sqrt X}{F}.}
\]

**Proof.** If `p` is ordinary, the congruence `p^e|1+hq^f` is either impossible or selects *one* residue class modulo `d_p p^{e-1}`. Thus the number of solutions in `[1,F]` is at most `F/(d_p p^{e-1})+1`. Summing the density terms gives

\[
\sum_{p>Y}\log p\sum_{e\ge2} \frac1{d_pp^{e-1}}
=\sum_{p>Y}\frac{\log p}{d_p(p-1)}\ll_qY^{-1/2},
\]

by Theorem A. The total boundary term is

\[
\frac1F\sum_{\substack{p^e\le X\\e\ge2}}\log p.
\]

Chebyshev's estimate gives `theta(t)=sum_{p<=t} log(p)=O(t)`, whence

\[
\sum_{\substack{p^e\le X\\e\ge2}}\log p
=\sum_{e=2}^{\lfloor\log_2 X\rfloor}\theta(X^{1/e})
\ll\sqrt X+X^{1/3}\log X\ll\sqrt X.
\]

Combining proves the theorem. QED.

**Corollary B1.** Take `Y=F^{1/4}`, `X=F^{3/2}`. Then for large `F`,

\[
\frac1F\sum_{f\le F}\mathcal E_{F^{1/4},F^{3/2}}(f)
\ll_q F^{-1/8}.
\]

In particular, the proportion of `f<=F` having *any* ordinary repeated prime-power event with `p>F^{1/4}` and `p^e<=F^{3/2}` is `O_q(F^{-1/8}/log F)`, since each event weighs at least `(1/4)log F`. This includes square factors up to `p<=F^{3/4}` and higher layers when `p` is smaller.

**Corollary B2.** Take `Y=F^{1/2}`, `X=F^{3/2}`. The average is `O_q(F^{-1/4})`. In this range only first-shell events `e=2` are possible, since `p^3>F^{3/2}`.

These are **averaged** estimates and exclude exceptional primes `p` with `v_p(q^{d_p}-1)>=2`. Their cutoff `X=F^{3/2}` is polynomial in `F`, while `1+hq^f` can be exponentially large in `F`. No assertion is made about prime-power factors beyond the cutoff.

## 4. Fixed input support: no fixed output-prime set can carry an ABC-sized defect

Let `S` be any fixed, nonempty finite set of primes. Suppose `a,b>0` are coprime and have all prime factors in `S`, with `c=a+b`. Put

\[
H=\max_{q\in S}v_q(ab)\ge1,
\qquad \nu_q=v_q(b)-v_q(a).
\]

For a fixed finite set `P` of primes disjoint from `S` define

\[
M_P(c)=\prod_{p\in P}p^{\max(0,v_p(c)-1)}.
\]

**Theorem C (consequence of Yu's p-adic logarithmic-form bound).** For every fixed `S,P`,

\[
\boxed{\log M_P(c)\ll_{S,P}\log(2+H)\ll_{S,P}\log\log(3c).}
\]

**Proof.** Let `p∈P`. Since `p∤ab`,

\[
 v_p(c)=v_p(1+b/a)=v_p\Bigl((-1)\prod_{q\in S}q^{\nu_q}-1\Bigr).
\]

The argument inside `v_p` is nonzero because `a+b>0`. The `p`-adic logarithmic-form theorem of Kunrui Yu bounds the valuation of a nonzero expression `prod alpha_i^{b_i}-1`, for **fixed algebraic bases and fixed p**, by `C log B` where `B>=max(3,|b_i|)`. Apply it to `alpha_0=-1`, `alpha_q=q`, coefficients `1,nu_q`, and `B=H+3`. It follows that `v_p(c)<=C_{S,p}log(H+3)` (uniform in the exponents). Multiplying by the fixed weights `log p` and summing over `P` proves the first bound.

To obtain the second, `c>=2^H` because one of the inputs is divisible by a prime power `q^H`; therefore `H<=log c/log 2`. Taking logarithms completes the proof. QED.

**Corollary C1 (restricted ABC, fixed repeated output support).** If every output prime satisfying `p^2|c` lies in the fixed finite set `P`, then

\[
\boxed{c\ll_{S,P}R\,(\log(3c))^{C_{S,P}}.}
\]

Consequently for every `epsilon>0` there is `K_{S,P,epsilon}` with `c<=K_{S,P,epsilon}R^{1+epsilon}` for *every* primitive triple with input support in `S` and repeated output support in `P`.

Indeed, `M=M_P`, and `c/R=M/rad(ab)<=M_P`. A fixed logarithmic power is absorbed in an arbitrarily small positive power of `R` by the standard inequality `c<=R (log c)^C`.

**Corollary C2 (rigorous escape of weighted mass).** Let `epsilon>0` and let `S,P` be fixed. Whenever an admissible triple has `c>R^{1+epsilon}`, then

\[
\boxed{
\sum_{\substack{p\mid c\\p\notin P}}(v_p(c)-1)\log p
>\frac{\epsilon}{1+\epsilon}\log c+
\log\operatorname{rad}(ab)-O_{S,P}(\log\log(3c)).
}
\]

**Proof.** `c>R^{1+epsilon}` and `R=D c/M` imply

\[
\log M>\frac{\epsilon}{1+\epsilon}\log c+\log D.
\]

Subtract `log M_P=O_{S,P}(loglog c)` using Theorem C. QED.

**Interpretation.** For any fixed input support `S`, a hypothetical infinite family of quality at least `1+epsilon` must move a *linear fraction* of its weighted powerful-part mass outside **every fixed finite output-prime set**. This is not a pointwise ABC proof: the constant in Yu's bound depends on `p`, and no sufficiently uniform estimate is known when the output-prime set grows with the input height.

## 5. An unconditional pointwise bound below a growing output-prime cutoff

The fixed-prime conclusion in Theorem C can be made **uniform when the prime p grows**, by keeping explicit control of the p-dependence in a published version of Yu's bound. The resulting exponent is deliberately conservative and independently follows from the auxiliary-field formula; it is not an assumed O(p) bound.

**Theorem E (pointwise small-output-prime budget).** Fix a nonempty finite input-prime set `S`. For any primitive `a+b=c` with all input prime factors in `S`, put `H=max_{q in S}v_q(ab)>=1`. Then an effective constant `C_S` exists such that for every prime `p not in S`,

\[
\boxed{v_p(c)\le C_Sp^2\log(H+3).}
\]

Consequently, for every `Y>=2`, writing

\[
M_{\le Y}(c)=\prod_{\substack{p\mid c\\p\le Y}}p^{v_p(c)-1},
\]

we have

\[
\boxed{\log M_{\le Y}(c)\le C'_S Y^3\log(H+3).}
\]

**Proof of uniform p-dependence.** The rational multiplicative bases are `mu_0=-1` and `mu_i=q_i` for the distinct primes `q_i` in `S`; the latter are multiplicatively independent. Since `p not in S`, all bases are p-adic units. In the explicit statement and proof in Alvarado–Koutsianas–Malmskog–Rasmussen–Vincent–West, *A robust implementation for solving the S-unit equation and several applications*, Theorem 3.1 and Corollaries 3.2–3.3, Yu's estimate has the shape

\[
 v_p\bigl((-1)\prod_{q\in S}q^{\nu_q}-1\bigr)
 < C_1^*(n,d_K,\mathfrak p)\,\Omega'\,\log B,
 \qquad B\ge\max(3,|\nu_q|),
\]

possibly with a ramification multiplier for the auxiliary field. Set `B=H+3` and `n=|S|+1`.

For odd `p`, one may work over `Q` when `p≡1 mod 4`. Otherwise one passes to `Q(i)`; if `p≡3 mod 4`, this is unramified and inert, so its residue degree is `f_p=2`. Thus the auxiliary field always has bounded degree, `e_p=1`, and `f_p<=2`. The explicit constants in their Section 3.3 have

\[
 C_1^*=(n+1)k_2k_3k_4,
 \quad k_3=\frac{p^{f_p}}{q^u}
 \left(\frac{d_K}{f_p\log p}\right)^{n+2}
 \log\max\{d_K,e\},
 \quad k_4\ll_S\log p.
\]

Here `q^u` is a positive integer (at least one), `k_2` depends on `n` and bounded tabulated constants, and `Omega'=h_p(-1) product_{q in S}h(q)` is `O_S(1)`: the fixed prime bases have fixed heights and the auxiliary residue degree is at most two. Hence

\[
 C_1^*\Omega'\ll_S\frac{p^{f_p}}{(\log p)^{n+1}}
 \ll_S p^2.
\]

The finitely many special primes (including `p=2,3`) are absorbed into `C_S`. Since

\[
(-1)\prod_{q\in S}q^{\nu_q}-1=-\frac{a+b}{a},
\]

its p-adic valuation is exactly `v_p(c)`. This proves the primewise bound.

To sum, use the elementary Chebyshev estimate `theta(Y)=sum_{p<=Y} log p=O(Y)`:

\[
\sum_{p\le Y}(v_p(c)-1)_+\log p
\le C_S\log(H+3)\sum_{p\le Y}p^2\log p
\le C_S Y^2\theta(Y)\log(H+3)
\ll_S Y^3\log(H+3).
\]

This completes the proof. **Note:** The quadratic p-dependence is a conservative bound extracted from the published auxiliary-field method. No uniform linear p-dependence is assumed here.

**Corollary E1.** Fix `0<delta<1/3` and set `Y=(log c)^{1/3-delta}`. Since `c>=2^H`,

\[
\boxed{
\log M_{\le (\log c)^{1/3-\delta}}(c)
\ll_{S,\delta}(\log c)^{1-3\delta}\log\log(3c)
=o(\log c).
}
\]

This holds **pointwise** for all primitive triples with fixed input support, including all aligned Wieferich channels and all valuation layers.

**Corollary E2 (a necessary condition for high-quality triples).** Let `epsilon>0`. If `c>R^{1+epsilon}` and `c` is sufficiently large (depending on `S`, `epsilon` and `delta`), then

\[
\boxed{
\sum_{\substack{p\mid c\\p>(\log c)^{1/3-\delta}}}
(v_p(c)-1)\log p
\ge\frac{\epsilon}{2(1+\epsilon)}\log c.
}
\]

Indeed, `log M>(epsilon/(1+epsilon))log c+log D` by `c/R=M/D`; subtract Corollary E1 and absorb the `o(log c)` term.

**Corollary E3 (restricted ABC with an expanding repeated-prime cutoff).** Fix `S`, `0<delta<1/3`, and `epsilon>0`. For every primitive triple with input support contained in `S` and with **every output prime p satisfying p^2|c lying below `(log c)^(1/3-delta)`**, we have

\[
\boxed{c\le K_{S,\delta,\epsilon}\,R^{1+\epsilon}.}
\]

Indeed, in that class `M=M_{<=Y}`, so `log M=o(log c)` uniformly. Because `log R=log c+log D-log M` and `D>=1`, it follows that `log c/log R ->1` uniformly over such triples as `c->infinity`. The finitely many small heights are absorbed in `K`. This is an **unconditional restricted ABC theorem**, imported from a published p-adic logarithmic-form estimate; it is not the unrestricted conjecture.

**Sharper residue-class option.** For `p≡1 mod 4`, the rational base field meets the auxiliary condition with residue degree one, yielding `v_p(c)<<_S p log(H+3)` by the same explicit formulas. These primes alone therefore satisfy a bound `O_S(Y^2 log(H+3))`. The square-root cutoff for this residue class does *not* extend to all primes from this auxiliary-field argument, so the global statement retains the conservative cubic exponent.

## 6. Exact collision identity for the moving prime-power tail

**Theorem D.** Let `U_f=1+hq^f`, `q>=2`, `h>=1`, and `1<=f<g`. Then

\[
\boxed{\gcd(U_f,U_g)=\gcd(U_f,q^{g-f}-1).}
\]

**Proof.** `U_g-q^{g-f}U_f=1-q^{g-f}`. Apply the Euclidean algorithm. QED.

If an integer `K>1` divides both outputs, then `K|q^{g-f}-1`, hence

\[
\boxed{g-f\ge\lceil\log_q(K+1)\rceil.}
\]

In a window of `F` exponents, at most `1+(F-1)/ceil(log_q(K+1))` output terms can contain that same divisible `K`. This is **deterministic separation** of repeated prime-power packets. For `U_f=1+2*3^f`, the simultaneous packet `K=5^2*7^2=1225` first recurs at `f=247,667,1087` (gap 420). The elementary lower bound only gives a gap of at least seven; the exact p-adic order structure explains the much larger period.

The collision identity does not constrain a prime power that occurs in only one output. Such isolated, very large prime-square factors remain the crucial obstruction.

## 7. What remains, without circularity

The elementary density sum from Theorem A is a sum of **fixed-p local limits**. It cannot be interchanged with the total weighted powerful-part sum over primes that move with `f`. A toy sequence `V_f=p_f^2` with distinct primes `p_f` makes the issue stark: every fixed prime's square-divisibility density is zero, while `log(V_f/rad(V_f))=log p_f` grows. This is an illustration of escaping mass, not a construction of ABC counterexamples.

Theorems B–E sharpen that issue:

1. Ordinary prime-square contacts with `p^e<=F^{2-delta}` are small **on average**.
2. A fixed set of output primes contributes only `O(loglog c)` to weighted powerful-part mass when the input support is fixed. In fact, the entire region `p<=(log c)^{1/3-delta}` contributes `o(log c)` **pointwise**, including all Wieferich primes.
3. Repeated occurrences of the same high prime-power packet at nearby exponents are constrained exactly by the gcd identity.

None bounds the moving exceptional part

\[
\sum_{\substack{p\mid c\\p\text{ varying with height}\text{or exceptional}}}(v_p(c)-1)\log p
\]

**pointwise** at a sublinear fraction of `log c`, as ABC requires in the fixed-input-support setting. The remaining task is a **uniform height-sensitive bound for large moving output prime powers**, not more local contact identities.

## 8. External sources, reproducibility and claim scope

- Kunrui Yu, *P-adic logarithmic forms and group varieties III*, Forum Mathematicum **19** (2007), 187–280, DOI [10.1515/FORUM.2007.009](https://doi.org/10.1515/FORUM.2007.009). The application in Theorem C uses Yu's logarithmic dependence on exponent height, not numerical constants computed here.
- An accessible statement with `ord_p(Theta-1)<C_1^* Omega log B`: [The Bounds of Baker–Wüstholz and Yu](https://www.uvm.edu/~cvincen1/files/preprints/vincent10.pdf), Theorem 3.1. 
- Alvarado, Koutsianas, Malmskog, Rasmussen, Vincent and West, *A robust implementation for solving the S-unit equation and several applications*, Theorem 3.1 and Corollaries 3.2–3.3, https://www.uvm.edu/~cvincen1/files/preprints/vincent10.pdf. The explicit quadratic `p`-dependence is derived from their constants and auxiliary quadratic field.
- Stewart–Yu, *On the abc conjecture II*, Duke Math. J. **108** (2001), states the established general bound `log c << R^{1/3}(log R)^3`; this note does not supersede it.
- Earlier Komorebi research checkpoint, *Weighted first-shell contact*, 24 October 2026: exact ordinary/exceptional local-density law, and previous tail `O(Y^{-1/3})`.

`verify.py` tests full prime-power congruence counts against independent direct modular exponentiation, the gcd identity, numerical partial order sums, and fixed-support examples. This does not replace Lean or a proof of Yu's theorem.
