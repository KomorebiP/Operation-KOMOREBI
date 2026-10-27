# Prime-Power Cartier Correction Closure

## Status

Candidate theorem with a complete algebraic proof given below and an independent finite exact verification script. The computation is supporting evidence, not the proof. No external literature/priority audit has been performed.

This block targets the open item in `Komorebi_Custom_GF_Cartier_Padic_Research_Report_0.3.pdf`: construction of a correction-state compiler for rational masks modulo `p^r`.

## Setup

Let `p` be prime, `r >= 1`, and `R_r = Z / p^r Z`. Let `A,B in Z[z]` satisfy

- `A(0) = B(0)`,
- `p` does not divide `B(0)`.

Let `F in R_r[[z]]` be the unique unit series with `F(0)=1` satisfying

`B(z) F(z) = A(z) F(z^p)`.

For `0 <= d < p`, let `Lambda_d` denote the Cartier section

`Lambda_d(sum_n c_n z^n) = sum_n c_{pn+d} z^n`.

Define the integral Frobenius-defect polynomial

`E_B(z) = (B(z)^p - B(z^p))/p in Z[z]`.

Its integrality is the coefficientwise freshman's-dream congruence modulo `p`.

## Theorem 1: exact correction-layer transition

For every integer `ell >= 1`, define

`q_ell = ceil((ell+1)/p)`,

`t_ell = p q_ell - (ell+1)`, so `0 <= t_ell <= p-1`.

Then for every polynomial `P(z)` and every Cartier digit `d`, in `R_r[[z]]`,

`Lambda_d(P F / B^ell)`

is equal to

`sum_{k=0}^{r-1} (-1)^k binom(q_ell+k-1,k) p^k`

`    * Lambda_d(P A B^{t_ell} E_B^k) F / B^{q_ell+k}`.

### Proof

From the defining Mahler equation,

`P F / B^ell = P A F(z^p) / B^{ell+1}`.

Write `ell+1 = p q_ell - t_ell`. Then

`B^{-(ell+1)} = B^{t_ell} (B^p)^{-q_ell}`.

By definition of `E_B`,

`B(z)^p = B(z^p) + p E_B(z)`.

Since `B(0)` is a `p`-adic unit, `B(z^p)` is invertible as a formal series. Hence modulo `p^r`,

`(B(z^p)+pE_B)^{-q_ell}`

`= B(z^p)^{-q_ell} (1 + p E_B/B(z^p))^{-q_ell}`

`= sum_{k=0}^{r-1} (-1)^k binom(q_ell+k-1,k) p^k`

`    * E_B(z)^k B(z^p)^{-(q_ell+k)}`.

Terms with `k >= r` vanish modulo `p^r`. Therefore

`P F/B^ell`

`= sum_{k=0}^{r-1} c_{ell,k} [P A B^{t_ell} E_B^k](z)`

`    * [F/B^{q_ell+k}](z^p)`

modulo `p^r`, where

`c_{ell,k}=(-1)^k binom(q_ell+k-1,k)p^k`.

Apply the coefficientwise Cartier identity

`Lambda_d(H(z) G(z^p)) = Lambda_d(H(z)) G(z)`

over any commutative coefficient ring. This gives the formula.

## Theorem 2: finite correction-layer closure

Set

`L_r = r - 1 + ceil(r/(p-1))`.

Then for every `1 <= ell <= L_r` and every `0 <= k < r`,

`q_ell + k <= L_r`.

### Proof

Write `s=ceil(r/(p-1))`, so `L_r=r-1+s`. Since `ell <= L_r`,

`q_ell <= ceil((L_r+1)/p) = ceil((r+s)/p)`.

The defining inequality `(p-1)s >= r` gives `r+s <= ps`; therefore `q_ell <= s`. Hence

`q_ell+k <= s+r-1 = L_r`.

Thus no denominator layer beyond `B^{-L_r}` is ever required at precision `p^r`.

## Theorem 3: finite polynomial-degree closure

Let

- `a = deg A`,
- `b = deg B`,
- `e = deg E_B` (take `e=0` when `E_B=0`),
- `T = max_{1 <= ell <= L_r} t_ell`,
- `C = a + T b + (r-1)e`,
- `D_r = max(b, ceil(C/(p-1)))`.

If every numerator polynomial in a state has degree at most `D_r`, then every numerator produced by every Cartier transition in Theorem 1 also has degree at most `D_r`.

### Proof

A branch numerator before Cartier has degree at most

`D_r + a + t_ell b + k e <= D_r + C`.

Cartier sectioning divides exponents by `p`, so its degree is at most

`floor((D_r+C)/p)`.

Since `C <= (p-1)D_r`, this is at most `D_r`.

## Corollary 4: finite linear representation modulo `p^r`

Represent a state by a tuple

`(P_1,...,P_{L_r}) in (R_r[z]_{<=D_r})^{L_r}`

standing for

`sum_{ell=1}^{L_r} P_ell(z) F(z)/B(z)^ell`.

Theorems 1--3 give a deterministic `R_r`-linear transition for every digit `d=0,...,p-1` on this finite module. The initial state is

`P_1=B`, `P_ell=0` for `ell>1`,

which represents `F`. The output functional is

`out(P_1,...,P_L) = sum_ell P_ell(0) B(0)^{-ell} mod p^r`.

If `n=d_0+d_1 p+...+d_m p^m`, then

`[z^n]F = out(T_{d_m} ... T_{d_1} T_{d_0} v_0)`.

Consequently the coefficient sequence modulo `p^r` has a finite linear representation and therefore a finite output automaton. A crude state bound is

`p^{r L_r (D_r+1)}`.

This bound is intentionally nonminimal; reachable-state minimization and valuation pruning can be much sharper.

## Recovery of the previous mod-p theorem

For `r=1`,

`L_1=1`.

For `ell=1`,

`q_1=1`, `t_1=p-2`.

Only `k=0` survives. Therefore Theorem 1 reduces exactly to

`Lambda_d(PF/B) = Lambda_d(P A B^{p-2}) F/B mod p`,

which is the rational-mask Cartier identity from the 0.3 report.

Also

`D_1 = max(b, ceil((a+(p-2)b)/(p-1)))`,

which is exactly the previous invariant degree bound.

Thus the prime-power construction is a strict filtered lift of the old compiler.

## Frobenius-defect packet interpretation

The finite polynomial

`E_B=(B^p-B(z^p))/p`

is the complete generator of the failure of one-layer denominator stabilization beyond characteristic `p`. Every higher correction term is a power `E_B^k` carrying the visible filtration weight `p^k`.

In operator language,

`T_d = T_d^(0) + p T_d^(1) + ... + p^{r-1} T_d^(r-1)`.

This is the direct bridge to the filtered p-adic reconstruction architecture in Arithmetic Packet Calculus IX: the mod-p Cartier machine is the depth-zero quotient, while prime-power lifting is controlled by a finite sequence of filtration-raising correction packets.

This does **not** prove the full Paper IX conjecture that every finitely presented arithmetic seed system has a canonical obstruction packet. It does give a concrete proved model of that mechanism for the rational-mask Mahler class.

## Exact finite verification

`verify_prime_power_cartier_bridge.py` independently computes coefficients by the defining recurrence

`B(z)F(z)=A(z)F(z^p)`

and by the correction-layer Cartier machine above.

The committed run uses:

- primes `2,3,5,7`,
- exponents `r=1,2,3,4`,
- 5 deterministic random masks per `(p,r)` pair,
- 5 curated masks,
- coefficient indices `0 <= n <= 120`,
- exact integer/modular arithmetic only.

Result: 85 mask/precision cases and 10,285 coefficient comparisons, with zero failures.

The bounded computation is not used as the universal proof. Its role is to audit conventions, digit order, correction signs, layer indexing, and degree/layer bounds.

## Claim boundary

What this block establishes, subject to ordinary proof checking:

1. An explicit prime-power Cartier correction identity.
2. An explicit finite denominator-layer bound at every fixed precision `p^r`.
3. An explicit finite numerator-degree bound.
4. A finite linear representation and finite output automaton for the rational-mask coefficient sequence modulo `p^r`.
5. Exact reduction to the previous mod-p theorem when `r=1`.
6. A finite Frobenius-defect packet generating all correction orders.

What is **not** established:

- literature novelty or priority;
- a precision-independent finite automaton simultaneously encoding all `r`;
- minimal state complexity;
- p-adic analytic convergence of the formal mask product at numerical p-adic arguments;
- the universal canonical-obstruction conjecture for arbitrary arithmetic seed systems.
