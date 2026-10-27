# RRCT v0.56 Formation-Cost Edge

## Objective

For route \(r\):

\[
J_r=L_r+\lambda C_r.
\]

A route is selected when its reduction in terminal loss is worth its additional structural cost.

## Pairwise break-even formula

For sufficient route \(r\) and cheaper route \(s\):

\[
L_r+\lambda C_r=L_s+\lambda C_s.
\]

Therefore:

\[
\boxed{
\lambda^*_{r\rightarrow s}
=
\frac{L_s-L_r}{C_r-C_s}
}
\]

For prices below \(\lambda^*\), the richer route is favored. For prices above it, the cheaper route is favored even when it introduces additional terminal error.

## Estimated thresholds

| Structure | Cost | Break-even \(\lambda^*\) |
|---|---:|---:|
| no workspace | 0.0 | — |
| flat | 1.0 | 0.992669 |
| pair 01\|23 | 2.5 | 0.398455 |
| pair 02\|13 | 2.5 | 0.398419 |
| pair 03\|12 | 2.5 | 0.398726 |
| overlap/full | 4.0 | 0.249756 |

## Observed regimes

\[
\lambda<0.03:
\quad
\text{overformation}
\]

\[
0.03\le\lambda\le0.22:
\quad
\text{minimal sufficient formation}
\]

\[
0.24\lesssim\lambda<0.40:
\quad
\text{overlap route suppressed first}
\]

\[
\lambda\approx0.40:
\quad
\text{pair hierarchies begin to collapse}
\]

The order of collapse follows the computed break-even thresholds.

## Goldilocks interpretation

The experiment exposes two competing pressures:

1. **Integration benefit:** richer workspaces reduce task loss on structurally demanding tasks.
2. **Formation cost:** richer workspaces require more communication, maintenance, or computational capacity.

The optimal architecture solves:

\[
r^*(e)
=
\arg\min_r
\left[L_r(e)+\lambda C_r\right].
\]

Thus workspace depth and coalition structure should be task-dependent rather than universally maximal.

## Boundary

This is not a universal cognitive law. The numeric thresholds depend on the supplied route costs, task losses, route library, cue noise, and training architecture. The reusable result is the break-even structure, not the specific price values.
