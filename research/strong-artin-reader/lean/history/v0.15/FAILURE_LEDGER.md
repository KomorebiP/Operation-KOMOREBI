# Failure ledger — Strong Artin Lean v0.15

## Development failures retained

### F1. Redundant rewrite in the recursive cardinality proof

The first strong-induction draft attempted to rewrite by the finrank generalization equation after the target had already been normalized to `Q.card ≤ Q₀.card + n`. Lean correctly reported that the pattern was absent.

**Resolution:** remove the redundant rewrite. No mathematical statement changed.

### F2. Empty-kernel finrank normalization

The first empty-start specialization expected simplification to rewrite

```text
finrank k (selectedKernel probe ∅)
```

to `finrank k V` automatically. It did not fire under the subtype coercion.

**Resolution:** explicitly rewrite `selectedKernel probe ∅ = ⊤`, then simplify `finrank_top`.

### F3. Module search-path failure

A first dependent-module compile was launched outside the portable workspace. `lake env` therefore did not populate the mathlib search path, and Lean reported unknown module prefixes.

**Resolution:** compile from the pinned portable workspace and add the fresh `.olean` directory inside the `lake env` shell.

### F4. Strong-induction argument order

In the arithmetic-constrained recursive theorem, the induction hypothesis expected the preserved-goodness proof before the finrank equality; the first call supplied them in the opposite order.

**Resolution:** reorder the two explicit arguments. The theorem then compiled.

## Classification

All failures were elaboration, normalization, or verifier-path issues. None refuted a mathematical lemma, introduced a weakened statement, or was counted as proof evidence.
