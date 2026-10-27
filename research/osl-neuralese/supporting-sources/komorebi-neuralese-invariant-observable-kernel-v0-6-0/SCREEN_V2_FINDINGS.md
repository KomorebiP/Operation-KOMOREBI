# Flat Connection Screen v2: findings and stop decision

**Author:** Komorebi P.

**Status:** developmental mechanism screen; execution integrity PASS; assay
validity PASS; no pilot promoted.

## Result

The untouched seed-137 screen used all nine anonymous relation cells, balanced
all eight D4 action strata, and evaluated only after checkpoint sealing.

| Arm | D4 depth 512 robust | Diamonds robust | Loop + suffix robust | Full holonomy median | Packet defect median |
|---|---:|---:|---:|---:|---:|
| supervised | 0.4258 | 1.0000 | 0.8715 | 0.3613 | 0.00242 |
| fresh v0.4 CR | 0.5352 | 1.0000 | 0.9097 | 0.1440 | 0.00083 |
| exact-flat v2 | **0.6836** | **1.0000** | **0.9479** | **0.0536** | **0.00065** |
| packet-flat v2 | 0.1172 | 0.7891 | 0.4931 | 0.4367 | 0.06855 |
| hybrid v2 | 0.2734 | 0.8594 | 0.4757 | 0.2045 | 0.04309 |
| shuffled packet | 0.2109 | 0.7969 | 0.5035 | 0.4052 | 0.03837 |

All native boundary rates were zero, and the exact compiled, quotient-curved,
suffix-visible-holonomy, collapse, and random-isometry controls behaved as
registered.

## What survived

Full-matrix anonymous relation pressure acted in the intended direction. From
the fresh CR comparator to exact-v2:

- median full holonomy fell from 0.1440 to 0.0536;
- depth-512 robust accuracy rose from 0.5352 to 0.6836;
- loop-plus-suffix robust joint correctness rose from 0.9097 to 0.9479;
- anchor-plane leakage spectral norm fell from a descriptive median 0.1705 to
  0.0922.

This strengthens the v1 observation that relation curvature is a genuine part
of the long-depth failure. It also shows that reducing curvature can improve
generic depth, although it does not remove all local generator error.

Exact-v2 nevertheless missed its pre-screen targets. Median holonomy was above
0.05, repeat-32 mean degradation remained 0.2917 with a worst suffix stratum of
0.50, and depth-512 accuracy remained far below confirmatory requirements.

## What failed

The multiscale packet objective was not merely insufficient; it was harmful.
Relative to supervised training, its held-out packet defect became about 28.3
times larger, depth-512 accuracy fell by 0.3086, and loop joint correctness fell
by 0.3785. It also lost every registered specificity comparison to the false-
equality arm.

The hybrid did not rescue the mechanism. It substantially underperformed the
exact-only arm on both loop behavior and depth, contradicting the pre-screen
decision rule.

## Ambient diagnosis

A posthoc float64 observability analysis stacked centered decoder maps after
all eight BFS normal-form suffixes. Every arm had numerical rank 12 at relative
thresholds (10^{-6}), (10^{-4}), and (10^{-2}). The median singular
spectrum had a large gap after rank seven, but the remaining five directions
were nonzero and became visible under future operators.

Thus the current network has no exact nontrivial observational kernel. Its
purported ambient quotient is only weakly observed, not invisible. The packet
loss was therefore trying to regulate a stiff, moving, effectively full-rank
observer while preserving endpoint behavior. Detaching the observer within a
step did not create an invariant ambient fiber across steps.

This diagnosis is consistent with the anchor-plane leakage audit:

| Arm | Median \(\lVert PMQ\rVert_2\) | Maximum \(\lVert PMQ\rVert_2\) |
|---|---:|---:|
| supervised | 0.7681 | 0.9937 |
| fresh v0.4 CR | 0.1705 | 0.2612 |
| exact-flat v2 | **0.0922** | **0.1406** |
| packet-flat v2 | 0.7557 | 0.9913 |

The packet arm did not make the ambient complement forward-invariant; future
operators could still rotate its contents directly into the semantic plane.

## Stop decision

The five-seed v0.5 pilot will not be run. The developmental screen falsified
the packet mechanism strongly enough that a confirmatory run would only spend
compute on a design already known to miss its own signatures. No threshold,
seed, or pilot result is being rewritten.

The next distinct hypothesis is an **Invariant Observable Kernel** block. It
must either architecturally fix a nontrivial quotient rank or preregister a
stable singular-gap rule, explicitly penalize generator leakage

\[
\lVert P M_g Q\rVert,
\]

and distinguish semantic relation flatness from permitted vertical holonomy.
Because that changes the hypothesis and model geometry, it belongs to v0.6,
not a post-outcome amendment of v0.5.
