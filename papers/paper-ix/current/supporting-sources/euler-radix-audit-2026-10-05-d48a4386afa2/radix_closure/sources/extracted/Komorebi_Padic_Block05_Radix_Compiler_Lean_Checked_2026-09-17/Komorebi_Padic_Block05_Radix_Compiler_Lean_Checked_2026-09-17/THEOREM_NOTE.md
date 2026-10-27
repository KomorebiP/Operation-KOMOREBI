# Block 05 theorem note

## 1. Target

Block 04 reduced quotient-barrier crossing to diagonal branches indexed by
`1 ≤ q ≤ Q`, with correction order

```text
k = pQ - q
```

and carry cost

```text
v_p ((pQ - 1).choose (pQ - q)).
```

The missing formal step was to prove the prime-base radix reduction and then
justify one exact representative per radix block.

## 2. Kummer radix descent

Let `p` be prime and write

```text
q - 1 = p*a + b,       0 ≤ b < p.
```

The complementary diagonal index has the exact decomposition

```text
pQ - q = (p - 1 - b) + p*(Q - 1 - a).
```

The top index similarly satisfies

```text
pQ - 1 = (p - 1) + p*(Q - 1).
```

For a base-`p` digit sum `s_p`, appending a low digit gives

```text
s_p(b + p*a) = b + s_p(a).
```

Consequently,

```text
s_p(q-1)       = b + s_p(a),
s_p(pQ-q)      = (p-1-b) + s_p(Q-1-a),
s_p(pQ-1)      = (p-1) + s_p(Q-1).
```

Mathlib's digit-sum form of Kummer's theorem states

```text
(p-1) v_p(n.choose k)
  = s_p(k) + s_p(n-k) - s_p(n).
```

Substitution cancels the entire low-digit contribution and yields

```text
(p-1) v_p((pQ-1).choose(q-1))
  = (p-1) v_p((Q-1).choose a).
```

Since `p` is prime, `p-1 > 0`, so natural-number cancellation proves

```text
v_p((pQ-1).choose(q-1))
  = v_p((Q-1).choose a).
```

Binomial symmetry converts the actual diagonal index `pQ-q` to `q-1`, giving

the checked theorem `barrierCarry_radix_descent`.

## 3. Exact radix representatives

The quotient identity

```text
(q-1)/p = a
```

holds exactly on

```text
p*a < q ≤ p*(a+1).
```

Thus the carry is constant throughout that interval. The visible part of the
branch cost is

```text
(pQ-q)(h+1),
```

which is nonincreasing in `q`. Therefore the maximal admissible point

```text
q_a = min(Q, p*(a+1))
```

minimizes total cost throughout block `a`.

A radix block is nonempty precisely when

```text
p*a < Q
```

or equivalently

```text
a ≤ floor((Q-1)/p).
```

This proves the checked compiler equivalence

```text
CrossesBarrier
  ↔ ∃ a ≤ floor((Q-1)/p), radixBarrierCost(p,h,Q,a) < r.
```

## 4. Finite minimum and Boolean compiler

`radixIndexSet` is the finite range

```text
{0, ..., floor((Q-1)/p)}.
```

`radixCostSet` maps every index to its exact representative cost, and
`minRadixBarrierCost` takes its nonempty minimum. The theorem
`binomialPadic_crossesBarrier_iff_minCost` proves

```text
CrossesBarrier ↔ minRadixBarrierCost < r.
```

Finally,

```text
radixCompilerCrosses p r h Q
  := decide (minRadixBarrierCost p h Q < r)
```

is kernel-proved correct by `radixCompilerCrosses_eq_true_iff`.

## 5. What this theorem does not prove

It does not yet formalize the Block 04 suffix-window early termination rule.
The current checked compiler scans every radix representative, not only the
short terminal suffix observed by the Python implementation.

It also does not prove the universal Paper IX obstruction-packet conjecture or
a precision-independent automaton.
