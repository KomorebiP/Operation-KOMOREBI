# Block 05 adversarial self-audit

## Claim card

For natural numbers `p,r,h,Q`, under

```text
p.Prime
0 < Q,
```

the Boolean

```text
radixCompilerCrosses p r h Q
```

is true exactly when the concrete binomial p-adic predecessor-edge system
crosses the quotient barrier `pQ`.

**Verdict:** proved as written under the displayed hypotheses.

## Dependency graph

```text
Mathlib Kummer digit-sum theorem
        +
Nat.digits low-digit decomposition
        ↓
binomial_padic_radix_descent
        +
Nat.choose symmetry
        ↓
barrierCarry_radix_descent
        +
quotient_eq_of_radix_block
        ↓
carry constant on each radix block
        +
visible order decreases with q
        ↓
barrierBranchCost_representative_min
        ↓
binomialPadic_crossesBarrier_iff_radix_range
        +
Finset minimum membership/minimality
        ↓
binomialPadic_crossesBarrier_iff_minCost
        ↓
radixCompilerCrosses_eq_true_iff
```

Every leaf is an internal checked theorem or a compiled mathlib theorem. Finite
Python results are not used as proof leaves.

## Obligation matrix

| Obligation | Status | Evidence |
|---|---|---|
| Low digit `b` remains in range | Passed | explicit `b < p` hypothesis |
| Complement low digit `p-1-b` remains in range | Passed | natural arithmetic proof |
| Kummer theorem has a prime instance | Passed | local `Fact p.Prime` |
| Cancellation by `p-1` is valid | Passed | `p.Prime.one_lt` |
| Diagonal choose index is within top index | Passed | `1 ≤ q ≤ Q`, `0 < p` |
| Diagonal and low choose indices are complementary | Passed | checked subtraction identity |
| Quotient block endpoints are exact | Passed | division inequalities in both directions |
| Terminal partial block is included | Passed | representative uses `min Q (...)` |
| Exact-multiple endpoint does not create an empty extra block | Passed | strict `p*a < Q` and `(Q-1)/p` |
| Representative carry equals descended carry | Passed | radix descent plus quotient theorem |
| Representative cost is minimal in block | Passed | common carry and antitone diagonal order |
| Finite cost set is nonempty | Passed | index `0`; barrier theorem separately requires `Q>0` |
| Finset image deduplication preserves the minimum | Passed | minimum taken over image values |
| Boolean reflection is exact | Passed | `decide_eq_true_eq` |
| Composite bases are covered | Out of scope | correctness theorem requires `p.Prime` |
| `Q=0` barrier correctness | Out of scope | theorem requires `0<Q` |
| Suffix early stop | Not addressed | next formal block |

## Boundary cases checked

The concrete Lean vector includes prime `p=2`, `Q=1`, exact radix boundaries,
partial terminal blocks, zero defect parameter `h=0`, and thresholds exactly at
and immediately above the finite minimum.

## Residual risk

This was a self-review, not an independent human referee report. Kernel checking
eliminates proof-term/type errors but does not establish that the definitions
model every broader informal objective of the p-adic program. The claim above
is tied to the exact definitions in this checkpoint.
