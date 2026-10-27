# Failure ledger — Strong Artin Lean v0.22

No failed attempt below is counted as proof evidence.

## 1. Explicit quotient equivalence did not elaborate

### Attempt

Define directly

```text
(raw presentation obstruction / relation syzygies) ≃ₗ[S] cotangent H1
```

using `LinearMap.quotKerEquivOfSurjective`.

### Failure

Lean failed to synthesize the quotient instance for the nested kernel-subtype module in the current elaboration context. Earlier variants also timed out while reducing the quotient type.

### Resolution

The final checkpoint proves the stronger operational data needed by later work:

- surjectivity;
- exact kernel;
- exactness of the sequence;
- equivalence under zero syzygies.

The explicit quotient `LinearEquiv` is not claimed as Lean-checked in v0.22.

## 2. Initial `map_single` coordinate proof simplified to `True`

### Attempt

Use

```text
simpa [relationDifferentialMap] using
  P.differentialsRelations.map_single r
```

inside the basis-coordinate theorem.

### Failure

The simplifier reduced the already-tagged simp theorem itself to `True`, producing a type mismatch.

### Resolution

The final proof first changes the goal explicitly to the underlying `Module.Relations.map` equality and then applies `map_single` without simplifying the theorem statement.

## 3. Finite-dimensional `finrank` formulation hit a typeclass diamond

### Attempt

State the rank formula over `[Field S]` using `LinearMap.finrank_range_add_finrank_ker`.

### Failure

The elaborator could not reconcile the semiring path inherited from the `CommRing`-based presentation API with the `DivisionRing` path expected by the finite-dimensional theorem. Some later attempts also exhausted heartbeats.

### Resolution

The final theorem uses the generic `HasRankNullity` cardinal-rank theorem and states the necessary universe lifts explicitly. No finite-dimensional numerical equality is claimed in the final source.

## 4. Direct `ker_eq_bot` rewrite failed on the nested linear map

### Attempt

Rewrite syzygy vanishing by `LinearMap.ker_eq_bot`.

### Failure

The elaborator did not infer the intended nested map through the presentation subtypes.

### Resolution

The final proof establishes injectivity and submodule equality directly, avoiding an ambiguous rewrite.

## 5. Scratch dimension and quotient modules

Development-only files testing direct quotient, `finrank`, and broad imports were excluded from the release. They contain failed or timed-out routes and are not part of the verified payload.
