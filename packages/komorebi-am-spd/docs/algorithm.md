# Algorithm guide

## 1. Normalized finite image

The reconstruction algorithms operate on a normalized finite raster with shape `H x W` or `H x W x C`, stored as `float64`, with a positive channel count. Supply finite floating-point values in `[0, 1]` when calling the array API. Nonnegative integer arrays are divided by their dtype's positive maximum, preserving constant and restricted-range brightness. Negative integers and floating-point values outside `[0, 1]` are rejected rather than silently rescaled.

Image loading preserves RGBA transparency and 16-bit grayscale. Normalized `.npy` inputs support arbitrary positive channel counts and are the route for scientific data normalized explicitly by the caller. Geometry proposals use grayscale directly, average two channels, or use the first three channels as an RGB guide; all channels remain part of fitting and residual closure.

Exact residual accounting does not preserve an original image file's container, metadata, color profile, integer dtype, or arbitrary scientific intensity scale. Decode to `.npy` to retain the normalized floating-point coordinates; ordinary image export may quantize or compress them. See [model-format.md](model-format.md).

## 2. Moving geometry packet core

`InfinitePacketReconstructor` starts with a constant packet and lazily generates candidate packets from a finite grammar. Candidate families include image-derived masks, polynomial and local cosine packets, DCT packets, affine and radial perturbations, morphology, compositional masks, and quadtree packets.

At each step the active span is globally refitted. The selected candidate is scored by its residual energy gain adjusted by a complexity proxy. The active packet count is bounded by `packet_budget`.

## 3. Singular Packet Decomposition seed

The packet core determines where useful geometric structure has already been found. SPD augments the core with local rank-one singular directions from dyadic and packet-derived supports. Every accepted direction is orthogonalized against the current span before projection.

The `singular_budget` bounds the number of added local modes.

An explicit `parameter_budget` caps the added singular or local-model scalar parameter proxy. It excludes the inherited geometry-core coefficient cost, which is reported separately. A zero explicit budget therefore retains the core and adds no downstream model. This preserves the benchmark's accounting convention; it is not a total-file-size cap or an entropy-coded bit budget.

## 4. Finite tree seeds

Two tree constructions are exposed:

- The Lagrange tree chooses between keeping a local model and splitting into children using a rate penalty.
- The exact-budget tree computes the nondominated cost-error frontier for the declared finite tree and selects the lowest local squared error within the integer parameter budget.

A global projection follows tree selection. This projection cannot increase least-squares error within the completed span.

## 5. Backward budget reopening

The portfolio starts from three retained seeds:

1. Greedy SPD
2. Lagrange tree
3. Exact-budget Pareto tree

For each declared reopened fraction, weak seed directions are removed until enough parameter budget has been freed. Moving local blocks are then proposed from fixed, residual, gradient, packet, and perturbed descendant regions. Every completed span is globally refitted.

The unchanged seed is retained as a candidate. Finite selection therefore cannot be worse than the retained seed under the raw, unclipped RMSE objective used by the selector, apart from numerical tolerance. This does not imply optimality over packet proposals that were never evaluated.

## 6. Exact residual archive

For the selected raw approximation `F_hat`, the package stores

```text
R_archive = F - F_hat
```

The reconstruction identity is therefore exact up to floating-point subtraction and addition:

```text
F = F_hat + R_archive
```

The display helper clips `F_hat` into `[0, 1]`. The residual archive always corresponds to the raw unbounded approximation, not the clipped display image.

## Complexity notes

The moving packet search and local SVD search are intentionally finite but can be expensive. Runtime depends on image dimensions, packet budget, candidate frontier size, local tree depth, rank range, and reopened fractions.

Use the quick preset for exploratory work. Use `paper-scale` when the larger declared budgets are appropriate. The paper-scale preset conducts a new packet search. Exact historical benchmark replay uses the recorded packet histories through `reproduce_paper_case` or `am-spd reproduce-paper`.


## 7. Portable decomposition and finite closure

`AMSpdModel` serializes the raw approximation, structured packet and tree metadata, and optional residual closure into a checksummed `.amspd` archive. Dense residual storage retains the full array. Sparse storage retains standard pixel coordinates and channel coefficients. Sparse storage with zero threshold gives the finite-raster coordinate closure stated in the paper without constructing a dense pixel-basis least-squares problem.

The model format separates the approximation from closure data. An approximation-only model cannot be decoded as an exact normalized source raster.
