# Theorem note: exact auxiliary elimination

Let

```text
K = coarseK r h
B = K / (p - 1) + 1
d = (B - 1) / p.
```

Natural subtraction gives `B - 1 = K / (p - 1)`.  Lean's total theorem

```text
Nat.div_div_eq_div_mul
```

then yields

```text
d = K / ((p - 1) * p) = K / (p * (p - 1)).
```

No positivity hypothesis is needed for this equality.  It therefore includes
Lean's totalized `p = 0` and `p = 1` cases, where both sides are zero.

Substitution into the Block 11 envelope gives

```text
2 * (K / (p - 1) + 1)
+ p
+ p * e * (e + 1) / 2,
```

where `e = K / (p * (p - 1))`.

Finally, `K ≤ r - 1`, so monotonicity of the envelope in `K` gives an `h`-free
bound.  These are upper envelopes only.  The exact executable counters remain
unchanged and are retained in the dependent certificate.
