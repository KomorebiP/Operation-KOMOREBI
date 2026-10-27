# Flat Connection Screen v1: retained developmental diagnosis

**Author:** Komorebi P.

This note records why the first v0.5 screen was not promoted to a pilot. It is
a developmental analysis, not a preregistered scientific result.

| Arm | Full holonomy median | Loop + suffix joint | Repeat-32 degradation | D4 depth 512 |
|---|---:|---:|---:|---:|
| fresh v0.4 CR | 0.1971 | 0.9306 | 0.4167 | 0.8086 |
| exact-flat v1 | **0.0689** | **0.9722** | **0.1250** | 0.8008 |
| packet-flat v1 | 0.2370 | 0.9097 | 0.3750 | 0.5898 |
| hybrid v1 | 0.0923 | 0.7500 | 0.7500 | 0.4102 |

Exact pressure acted on the intended failure: it reduced full-space angular
holonomy and improved repeated null-loop behavior without materially changing
generic depth-512 execution. The remaining deep error is therefore not just
relation curvature; inaccurate local generators remain a separate bottleneck.

The original packet loss controlled only a single application of

\[
J D\,S\,(L-R)B
\]

through a learned anchor matrix \(B\), learned decoder \(D\), and suffixes no
longer than three steps. Because all three observers received gradients, the
model could move the observer around a residual. Orthogonal recurrence then
preserved that residual until a later suffix rotated it back into a decodable
direction. A small one-step packet loss therefore did not imply long-horizon
packet flatness.

The second-screen correction freezes the observer side of the structural
gradient and penalizes repeated holonomy:

\[
H=R^\mathsf TL,
\qquad
\frac{\lVert JD\,S\,(H^k-I)B\rVert_F^2}
{\operatorname{stopgrad}(\lVert JD\,SB\rVert_F^2+\tau)},
\qquad
k\in\{1,2,4,8,16\}.
\]

It also delays packet pressure until the ordinary semantic observer has begun
to form, covers all eight BFS normal-form suffixes and all nine non-tree
relation cells, and leaves \(k=32\) untouched for extrapolation.

The first screen also revealed a bank-design error: fixed even-length binary
words can realize only one parity half of D4. The corrected held-out diamonds
use adjacent even/odd length pairs and balance all eight exact action
signatures. The original output remains available only as transparent
developmental history.
