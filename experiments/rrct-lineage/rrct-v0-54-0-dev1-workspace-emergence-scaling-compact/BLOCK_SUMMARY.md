# RRCT v0.54 — Workspace-Emergence Scaling

## Status

- **Version:** `0.54.0.dev1`
- **Frozen holdout:** `V054_HOLDOUT_ENDPOINTS_NOT_MET`
- **Frozen endpoints:** **13 of 16 passed**
- **Core scaling result:** supported with a revised reliability boundary
- **Strict pre-holdout threshold forecast:** partially falsified
- **Valence or self-preservation model:** absent

## Question

Within the supplied two-level hierarchy from v0.53, how do bottleneck dimension, hidden width, and terminal-training scale control when local and global workspace representations appear without intermediate workspace labels?

“Emergence” requires more than task success. A model must simultaneously pass:

1. terminal action accuracy >= .98;
2. local-A, local-B, and global linear-probe accuracy >= .95;
3. local-A, local-B, and global causal-transplant accuracy >= .95;
4. global-workspace ablation accuracy <= .15.

## Main result

The transition is abrupt and probabilistic.

- A **one-dimensional bottleneck never emerged**, even after 2.248 billion parameter-sample updates.
- Two- and four-dimensional bottlenecks showed seed-sensitive transitions from failure to fully causal latent workspaces.
- Four dimensions reached reliable emergence substantially earlier than two dimensions in the frozen configurations.
- More width reduced the number of optimization steps needed over part of the tested range, but did not remove seed sensitivity near the frontier.

## Frozen holdout

| Configuration | Emergence rate | Action | Probe | Transplant | Cut |
|---|---:|---:|---:|---:|---:|
| d1, width 64, 2400 steps | 0/4 | .0834 | .0800 | .0810 | .0450 |
| d2, width 32, 200 steps | 0/4 | .5208 | .5396 | .5065 | .0451 |
| d2, width 32, 400 steps | 2/4 | .7624 | .7643 | .7536 | .0457 |
| d2, width 32, 800 steps | 3/4 | .9660 | .9675 | .9651 | .0447 |
| d4, width 16, 200 steps | 1/4 | .8979 | .9537 | .8914 | .0455 |
| d4, width 16, 400 steps | **4/4** | **.9971** | **.9995** | **.9967** | .0446 |
| d4, width 16, 800 steps | **4/4** | **1.0000** | **1.0000** | **1.0000** | .0448 |

The frozen d2 predictions were too optimistic. The preregistered expectations of at least 3/4 emergence at 400 steps and 4/4 at 800 steps failed. No thresholds were changed.

## Post-hoc frontier extension

The failed d2 frontier was extended after the frozen result:

| Configuration | Emergence rate | Action | Probe | Transplant | Cut |
|---|---:|---:|---:|---:|---:|
| d2, width 32, 1200 steps | **4/4** | **.9996** | **.9995** | **.9991** | .0452 |

Thus, in the tested fresh seeds, reliable two-dimensional emergence appeared by 1200 updates, while the four-dimensional system reached it by 400.

## Empirical scaling law

The development fit used:

\[
P(E=1)=\sigma\!\left(
 b_0+b_S\log_2 S+b_H\log_2 H+b_{HH}(\log_2H)^2+b_D\log_2D
\right),
\]

where:

- \(S\) is terminal-training steps;
- \(H\) is hidden width;
- \(D\) is bottleneck dimension;
- \(E\) is full workspace emergence.

The development-only model achieved leave-one-seed-out AUC **0.974**. On fresh formula-domain holdout points it retained AUC **0.900**, but its calibration was too confident near the d2 boundary.

A post-hoc combined descriptive fit is:

\[
\operatorname{logit}P(E=1)
\approx
-34.382
+2.868\log_2S
+1.239\log_2H
+0.00157(\log_2H)^2
+2.974\log_2D.
\]

This is an empirical description of this architecture and task, not a universal cognitive scaling law.

## Cohort reliability correction

If a configuration has per-seed emergence probability \(p\), the probability that all \(n\) independently initialized seeds emerge is approximately:

\[
P(\text{all }n)=p^n.
\]

For target cohort reliability \(q\), use per-seed probability:

\[
p=q^{1/n}.
\]

The corresponding scale estimate is:

\[
S_{q,n}(D,H)
=
2^{\frac{
\operatorname{logit}(q^{1/n})-b_0-b_H\log_2H-b_{HH}(\log_2H)^2-b_D\log_2D
}{b_S}}.
\]

For d2, width 32, and four seeds at 95% all-seed reliability, the revised formula predicts approximately **1256 updates**. The post-hoc 1200-step run achieved 4/4 emergence.

## Exact interpretation

The result supports:

> **Within a supplied nested architecture, terminal-only training produces a phase-transition-like onset of causally modular workspace semantics once representational dimension and optimization scale cross a task-dependent frontier.**

It does not support:

- spontaneous discovery of the hierarchy;
- spontaneous coalition selection;
- a universal emergence constant;
- biological brain equivalence;
- functional awareness;
- subjective experience, consciousness, valence, or moral status.

## Next direction

The next experiment should expose several possible coalition graphs and workspace depths simultaneously, charge for communication and workspace use, and ask whether terminal training selects the appropriate hierarchy as task synergy and population size increase.


## Release validation

- Focused scaling tests: **5 passed**
- Pre-outcome sealed files: **9 verified unchanged**
- Frozen point files: **28**
- Post-hoc boundary point files: **4**
- Representative frozen retraining replays: **2 scientifically exact**
- Post-hoc 1200-step retraining replays: **4 scientifically exact**
- Release checks: **52 of 52 passed**
- Complete 28-cell retraining replay: **not claimed**

The frozen scientific status remains failed because three preregistered reliability endpoints did not pass. Release verification means that the evidence, failure status, formula, post-hoc extension, and integrity controls are internally consistent and reproducible at the tested replay points.
