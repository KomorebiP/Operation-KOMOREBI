# Prime-Power Cartier Bridge, Block 02

## Status

This block continues the fixed-precision rational-mask Cartier lift proved in Block 01. It adds:

1. optimality of the original contiguous correction-layer bound;
2. an exact valuation formula for every correction branch;
3. a defect-valuation sharpened layer bound;
4. an exact valuation/binomial-pruned layer graph;
5. least layer-specific numerator-degree bounds;
6. an implemented sparse prime-power Cartier compiler;
7. exact reachable-state enumeration and Moore minimization when the state set is computationally manageable;
8. a necessary-and-sufficient Frobenius-defect obstruction theorem for preserving the literal one-layer Cartier normal form from one p-adic precision to the next.

No literature or priority claim is made. The computation audits the formulas and implementation; it is not substituted for the proofs below.

---

## 1. Setup

Let `p` be prime, `r >= 1`, and work in

`R_r = Z / p^r Z`.

Let `A,B in Z[z]` satisfy

- `A(0) = B(0)` in `R_r`,
- `p` does not divide `B(0)`.

There is a unique unit series `F in R_r[[z]]`, `F(0)=1`, satisfying

`B(z) F(z) = A(z) F(z^p)`.

For `0 <= d < p`, define the Cartier section

`Lambda_d(sum_n c_n z^n) = sum_n c_{pn+d} z^n`.

Define the integral Frobenius-defect polynomial

`E_B(z) = (B(z)^p - B(z^p))/p in Z[z]`.

The divisibility by `p` follows coefficientwise from the freshman's-dream congruence.

For a nonzero integer polynomial `H`, write

`v_p(H) = min_j v_p([z^j]H)`.

Set `v_p(0)=infinity`.

---

## 2. Exact correction-layer transition (Block 01 theorem retained)

For `ell >= 1`, set

`q_ell = ceil((ell+1)/p)`,

`t_ell = p q_ell - (ell+1)`,

so `0 <= t_ell <= p-1`.

For every polynomial `P` and digit `d`, in `R_r[[z]]`,

`Lambda_d(P F / B^ell)`

is

`sum_{k=0}^{r-1} (-1)^k binom(q_ell+k-1,k) p^k`

`    * Lambda_d(P A B^{t_ell} E_B^k) F / B^{q_ell+k}`.

### Proof

From the Mahler equation,

`P F/B^ell = P A F(z^p)/B^{ell+1}`.

Write `ell+1=p q_ell-t_ell`, hence

`B^{-(ell+1)} = B^{t_ell}(B^p)^{-q_ell}`.

Since

`B^p = B(z^p)+pE_B`,

expand

`(B(z^p)+pE_B)^{-q_ell}`

with the negative-binomial series modulo `p^r`. Terms with `k>=r` contain `p^r` and vanish. Apply

`Lambda_d(H(z)G(z^p))=Lambda_d(H(z))G(z)`.

---

## 3. Original contiguous layer bound and its optimality

Block 01 used

`L_r = r-1 + ceil(r/(p-1))`.

It satisfies

`q_ell+k <= L_r`

for every `1 <= ell <= L_r` and every `0 <= k < r`.

### New theorem: `L_r` is the smallest contiguous all-branch bound

Suppose an integer `L` has the property

`q_ell+k <= L`

for every `1 <= ell <= L` and every `0 <= k < r`.

Then

`L >= r-1 + ceil(r/(p-1))`.

Thus the Block 01 bound is optimal among bounds that retain every formal correction order `0,...,r-1` and use a contiguous layer interval `{1,...,L}`.

### Proof

Closure at the top layer `ell=L` and top correction `k=r-1` requires

`ceil((L+1)/p) + r-1 <= L`.

Put

`s=L-r+1`.

Then

`ceil((r+s)/p) <= s`,

so

`r+s <= ps`,

hence

`s >= ceil(r/(p-1))`.

Therefore

`L >= r-1+ceil(r/(p-1))`.

The reverse inequality is Block 01's closure proof.

---

## 4. Exact p-adic valuation of a correction branch

Let

`h = v_p(E_B)`

when `E_B != 0`.

The polynomial weight on correction order `k` at layer `ell` is

`W_{ell,k}`

`= (-1)^k binom(q_ell+k-1,k) p^k E_B^k`.

### Theorem: exact branch-content valuation

If `E_B != 0`, then

`v_p(W_{ell,k})`

`= k(1+h) + v_p(binomial(q_ell+k-1,k))`.

### Proof

Write

`E_B=p^h E_0`

with `E_0 mod p` nonzero in `F_p[z]`. Since `F_p[z]` is an integral domain,

`E_0^k mod p != 0`.

Therefore

`v_p(E_B^k)=kh`.

Multiplication by the integer scalar

`p^k binom(q_ell+k-1,k)`

adds exactly

`k+v_p(binomial(q_ell+k-1,k))`.

Because `A(0)` and `B(0)` are p-adic units, multiplication by `A B^{t_ell}` does not increase polynomial p-content: its reduction modulo `p` is nonzero, so the product with the nonzero reduction of the normalized branch is nonzero in `F_p[z]`.

Hence this is also the exact content valuation of the full pre-Cartier branch kernel.

### Exact branch-pruning criterion

The correction branch `k` is identically zero modulo `p^r` iff

`k(1+h) + v_p(binomial(q_ell+k-1,k)) >= r`.

If `E_B=0`, every branch with `k>=1` vanishes at every precision.

---

## 5. Defect-valuation sharpened layer bound

Ignoring the additional nonnegative binomial valuation for the moment, a branch can survive only if

`k(1+h) < r`.

Define

`K_{r,h} = floor((r-1)/(h+1))`

when `E_B != 0`, and set `K=0` when `E_B=0`.

Then every surviving correction has `0 <= k <= K`.

Define

`L_{r,h} = K + ceil((K+1)/(p-1))`.

### Theorem: valuation-sharpened closure

For every `1 <= ell <= L_{r,h}` and every `0 <= k <= K`,

`q_ell+k <= L_{r,h}`.

Therefore every genuinely surviving correction layer modulo `p^r` lies in

`{1,...,L_{r,h}}`.

### Proof

Put

`s=ceil((K+1)/(p-1))`,

so `L=K+s`. The defining inequality gives

`K+1 <= (p-1)s`,

hence

`K+s+1 <= ps`.

Therefore

`q_ell <= ceil((L+1)/p) <= s`,

and

`q_ell+k <= s+K=L`.

### Consequences

- Generic defect `h=0` recovers the original bound because `K=r-1`.
- Extra defect divisibility immediately reduces the number of required denominator layers.
- `E_B=0` gives `K=0`, `L=1`: exact one-layer closure at every precision.

The exact binomial valuation can prune further than `L_{r,h}`.

---

## 6. Canonical pruned layer graph

At fixed `(A,B,p,r)`, start from layer `1` and draw a directed edge

`ell -> q_ell+k`

for every correction order `k` whose branch-content valuation is `< r`.

Equivalently, retain only nonzero branch kernels modulo `p^r`.

Let `S_{A,B,p,r}` be the smallest layer set containing `1` and closed under these nonzero edges.

Then

`S_{A,B,p,r} subseteq {1,...,L_{r,h}} subseteq {1,...,L_r}`.

This is the layer graph used by the Block 02 compiler.

It is not claimed that every layer in the graph is visited by the orbit of one particular starting state. It is the exact layer closure required by the retained correction formula on the compiler's polynomial state module.

---

## 7. Layer-specific degree closure

Block 01 used one global degree bound. Block 02 replaces that with a least fixed point over the pruned graph.

For an active edge

`e=(ell,k) -> j`,

let

`C_e = deg( A B^{t_ell} W_{ell,k} mod p^r )`.

Choose integer degree bounds `D_ell` satisfying

`D_1 >= deg B`

and, for every active edge,

`D_j >= floor((D_ell+C_e)/p)`.

### Proposition: least finite degree profile

Starting with

`D_1=deg B`,

all other `D_ell=-1`,

and repeatedly applying the inequalities above reaches a least fixed point in finitely many steps.

### Proof

The iteration is monotone. The Block 01 global degree theorem supplies a finite coordinatewise upper bound. Therefore the iteration takes place in a finite product of finite integer intervals and can increase only finitely many times.

The resulting degree profile is sufficient because a branch numerator has degree at most

`D_ell+C_e`,

and Cartier sectioning reduces degree to at most

`floor((D_ell+C_e)/p)`.

This profile is minimal among bounds obtained solely from these degree-propagation inequalities.

---

## 8. Sparse finite linear representation

Use basis vectors

`z^j F/B^ell`

only for

- `ell in S_{A,B,p,r}`,
- `0 <= j <= D_ell`.

Each Cartier digit has an explicitly computed sparse matrix over `Z/p^r Z` on this basis.

The starting vector is `F=(B/B)F`, so layer `1` contains numerator `B`.

The output functional is

`out((P_ell)_ell) = sum_ell P_ell(0) B(0)^(-ell) mod p^r`.

For

`n=d_0+d_1 p+...+d_m p^m`,

`[z^n]F = out(T_{d_m}...T_{d_0}v_0)`.

Hence the coefficient sequence modulo `p^r` has a finite sparse linear representation.

Because the coefficient ring and module are finite, the reachable orbit is a finite deterministic output automaton. When that reachable set is small enough to enumerate, ordinary Moore refinement produces the exact minimal deterministic output automaton for the enumerated machine.

The implementation is `prime_power_cartier_compiler.py`.

---

## 9. Exact Frobenius-defect obstruction theorem

The characteristic-p compiler has the literal one-layer formula

`Lambda_d(PF/B)`

`= Lambda_d(P A B^{p-2}) F/B`.

At higher precision this formula usually fails and correction layers appear.

### Theorem: exact criterion for preserving the literal one-layer normal form

For fixed `r>=1`, the following are equivalent:

1. for every polynomial `P` and every digit `d`, the literal characteristic-p one-layer formula above remains valid modulo `p^r`;
2. it is valid for `P=1` and every digit `d`;
3. `p E_B = 0 mod p^r` coefficientwise;
4. `E_B = 0 mod p^{r-1}` coefficientwise;
5. `B(z)^p = B(z^p) mod p^r`.

### Proof

Only `(2) => (3)` needs explanation beyond the formulas already proved.

The family of all Cartier sections jointly reconstructs a formal series:

`X(z)=sum_{d=0}^{p-1} z^d (Lambda_d X)(z^p)`.

Thus equality after every digit section is equivalent to equality before sectioning.

For `P=1`, the desired one-layer identity is equivalent to

`F/B = A B^{p-2} (F/B)(z^p)`.

Using `BF=A F(z^p)`, the difference between the two sides is

`A F(z^p) [1/B^2 - B^{p-2}/B(z^p)]`

`= A F(z^p) [B(z^p)-B^p]/[B^2 B(z^p)]`

`= -p E_B * U(z)`,

where

`U(z)=A F(z^p)/[B^2 B(z^p)]`

is a unit because its constant term is p-adically invertible.

Multiplication by a unit preserves coefficientwise divisibility by `p^r`. Therefore the one-layer identity holds modulo `p^r` iff

`pE_B=0 mod p^r`,

which is equivalent to the other conditions.

### Corollary: exact one-layer stabilization depth

If `E_B != 0` and

`h=v_p(E_B)`,

then the literal mod-p one-layer compiler survives unchanged precisely through precisions

`p^r` with `r <= h+1`.

Thus the maximal exponent is

`rho_p(B)=h+1`.

If `E_B=0`, set `rho_p(B)=infinity`.

---

## 10. A genuine successive obstruction packet

Assume the literal one-layer normal form holds modulo `p^s`. Equivalently,

`E_B` is divisible by `p^{s-1}`.

Define

`O_s(B) = p^{-(s-1)} E_B mod p in F_p[z]`.

### Corollary: next-precision obstruction

The one-layer normal form lifts from precision `p^s` to precision `p^{s+1}` iff

`O_s(B)=0`.

### Proof

The next lift exists in the same one-layer normal form iff

`E_B=0 mod p^s`.

After dividing by the already-known factor `p^{s-1}`, this is exactly the vanishing of `O_s(B)` modulo `p`.

### Claim boundary

This is a canonical finite obstruction packet for **preserving this specific rational-mask one-layer Cartier normal form**.

It is not a proof of Paper IX's unrestricted conjecture that every finitely presented arithmetic seed system admits a canonical obstruction packet for arbitrary lifts. In fact, the formal series `F` itself always lifts uniquely here because `B(0)` is a unit; the obstruction concerns preservation of the compressed one-layer representation, not existence of the underlying series.

That distinction is essential.

---

## 11. Kummer carry form of the correction graph

The only nontrivial scalar valuation in a branch is

`v_p(binomial(q_ell+k-1,k))`.

By Kummer's theorem this is exactly the number of carries in base `p` when adding

`k + (q_ell-1)`.

Write this carry count as

`c_p(k,q_ell-1)`.

Then the exact active-edge criterion becomes

`k(1+h) + c_p(k,q_ell-1) < r`.

Thus the prime-power correction graph has a literal radix-carry description:

- `k(1+h)` is the visible Frobenius-defect filtration cost;
- `c_p(k,q_ell-1)` is the additional Kummer carry cost;
- a branch survives exactly when the total cost is below the available precision `r`.

This identifies the new correction-state compiler with the older carry/Kummer architecture at the level of the exact pruning law, not merely by analogy.

### Immediate regime

If

`K=floor((r-1)/(h+1)) <= p-2`,

then

`L_{r,h}=K+1`.

Layer `1` has `q_1=1`, so its branches `k=0,...,K` have no Kummer carries and reach every layer

`1,...,K+1`.

Therefore in this regime the exact layer set is already forced to be

`{1,...,K+1}`.

Outside this regime, higher-layer Kummer carries can delete some of the edges that would attain the valuation-only upper bound; the exact graph is computed by the carry criterion above.

The implementation now uses this carry count as an early branch-pruning test before constructing the full polynomial kernel.

---

## 12. Exact computation audit

### Sparse compiler regression

`verify_sparse_prime_power_compiler.py` compares the sparse Cartier compiler against an independent direct recurrence for

`B(z)F(z)=A(z)F(z^p)`.

Retained run:

- primes `2,3,5,7`;
- precision exponents `r=1,...,5`;
- 6 deterministic random masks per `(p,r)` plus 7 curated masks;
- coefficient range `0 <= n <= 180`;
- 127 mask/precision cases;
- 22,987 coefficient comparisons;
- zero mismatches.

State-space sharpening in that run:

- strict dimension reduction in 111 of 127 cases;
- strict layer reduction in 51 cases;
- mean sharpened/original dimension ratio approximately `0.50418`;
- minimum ratio approximately `0.07143`.

### Obstruction criterion audit

`verify_obstruction_packet.py` checks the stabilization-depth criterion on

- primes `2,3,5,7,11`;
- 225 masks;
- precisions through exponent `7`;
- 1,575 exact precision checks;
- zero failures.

### Branch valuation audit

`verify_branch_valuation.py` checks the exact branch-content valuation identity on

- primes `2,3,5,7`;
- 20 deterministic masks per prime;
- correction/precision range through `r=6`;
- 9,389 exact checks;
- zero failures.

An earlier, much larger naive version of this auxiliary audit timed out because it recomputed polynomial powers in deeply nested loops. That timeout was a harness-performance failure, not a mathematical failure. The retained version caches the powers and completes successfully.

### Kummer/carry graph audit

`verify_kummer_carry_graph.py` compares the specific binomial valuation in every correction edge with a direct base-`p` carry count.

Retained run:

- primes `2,3,5,7,11,13`;
- `1 <= q <= 59`;
- `0 <= k <= 79`;
- 28,320 Kummer valuation/carry comparisons;
- 33,471 active-edge criterion comparisons through `r=20` and synthetic defect valuations `h=0,...,4`;
- zero failures.

Kummer's theorem is a classical input; the finite audit checks conventions and the specialized indexing used here.

### Reachable/minimal automaton audit

`verify_reachable_minimization.py` enumerates five manageable reachable machines, minimizes them by Moore refinement, and compares both the reachable and minimized automata against direct coefficients through `n=500`.

- 5 automata;
- 2,505 coefficient checks;
- zero failures.

Two examples showed strict output-state minimization; three were already minimal among their reachable states.

---

## 13. What Block 02 establishes

Subject to ordinary proof review, this block establishes:

1. the Block 01 correction-layer formula;
2. optimality of the original contiguous all-branch layer bound;
3. exact p-adic valuation of each correction branch;
4. a defect-valuation sharpened layer bound;
5. exact binomial/valuation branch pruning;
6. the exact Kummer carry form of the active-edge criterion;
7. a least layer-specific degree profile;
8. an implemented sparse fixed-precision Cartier compiler modulo `p^r`;
9. exact reachable-state and Moore minimization routines with explicit resource caps;
10. a necessary-and-sufficient criterion for unchanged one-layer lifting;
11. a canonical successive obstruction polynomial for that normal-form lifting problem.

## 14. What remains open

This block does **not** establish:

- literature novelty or priority;
- a precision-independent finite automaton simultaneously valid for all `r`;
- a universal obstruction packet for arbitrary arithmetic seed systems;
- optimal linear-representation dimension;
- a closed formula for the exact binomial-pruned layer graph in all `(p,r,h)` regimes;
- a Lean-checked formalization;
- the prime-independent arithmetic spine conjecture from Paper IX.

The current container still does not provide a Lean/Lake executable, so no checked Lean proof is claimed.
