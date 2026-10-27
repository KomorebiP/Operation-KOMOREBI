# Komorebi Cross-Radix Rigidity Lean v0.3.0

Pinned formal checkpoint for the cross-radix cyclotomic/projector algebra program.

## Proof environment

- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- strict compile gate: `-DwarningAsError=true`
- representative `#print axioms`: only `propext`, `Classical.choice`, `Quot.sound`
- no `sorry`, `admit`, or custom `axiom` declarations found by the release scan

## Main v0.3 results

Fix `T > 0`. Canonical width coordinates are `W_g(c)=1` iff `g | c`, for divisors `g,c | T`.

1. Primitive shells `E_c` are pairwise orthogonal idempotents, sum to the identity, and form an operator basis.
2. Every idempotent in the complete diagonal projector algebra is uniquely a subset-sum of primitive shells. Hence the number of idempotents is `2^(tau(T))`.
3. Möbius inversion recovers shells from widths:
   `E_c = sum_{r | T/c} mu(r) W_{c r}`.
4. Canonical widths multiply by lcm and form the divisor-poset zeta basis.
5. The prime-power widths `W_(p^j)` are the unique least separating family.
6. Every shell has the explicit Boolean formula
   `E_c = product_{q | T, q prime-power} (W_q if q | c else 1-W_q)`.
7. The prime-power widths generate the full coordinate algebra as an actual algebra-adjoin theorem; every algebra-generating family of canonical widths must contain all of them.
8. The exact minimal generator count is
   `# {q | T : q prime-power} = Omega(T) = sum_p v_p(T)`.
9. Prime-local normal forms:
   - `W_g = product_{p | T} W_(p^(v_p(g)))`;
   - `E_c = product_{p | T} L_(p,v_p(c))`, where `L_(p,a)` is the adjacent valuation difference below the top exponent and the top threshold at `a=v_p(T)`.
10. Divisor labels are canonically equivalent to bounded valuation vectors
    `{c : c | T} ≃ product_{p | T} {0,...,v_p(T)}`.
11. The coordinate algebra is algebra-equivalent to the function algebra on that valuation product.
12. Exact complexity ledger:
    - minimal canonical generator complexity: `Omega(T)`;
    - spectral/algebra dimension: `prod_{p | T} (v_p(T)+1) = tau(T)`;
    - idempotent complexity: `2^(tau(T))`.

## Boundary

The Bell generalized Cobham theorem used earlier to pass from two multiplicatively independent regular structures to root-of-unity rationality remains an external theorem, not a Lean theorem in this archive. Everything listed above is downstream finite algebra/arithmetic and is checked directly in Lean.

The prior integral obstruction is also retained: a naive all-radix integral normal form fails because radix-local saturation defects can appear, already for the square sequence.

See `AUDIT.json` and `logs/` for hashes and strict-check records.

## v0.4 generator-complexity separation

The width-compatible generator count `Omega(T)` is not the abstract algebra-generator number.

Define the global spectral label `L(c)=c` (viewed in `C`). Lean now proves every primitive shell by the explicit Lagrange formula

`E_c = product_{d != c} (L-d)/(c-d)`.

Hence `Alg<L> = A_T`: one unrestricted spectral observable generates the entire diagonal coordinate algebra. For `T>1`, Lean also proves that the empty generator set does not generate it. Therefore:

- unrestricted algebra-generator number: exactly `1` for `T>1`;
- unique least canonical-width generator family: all prime-power thresholds, of size `Omega(T)`.

This distinction is structural: `Omega(T)` measures the cost of retaining canonical width/projector semantics, not a limitation of the abstract semisimple algebra.
