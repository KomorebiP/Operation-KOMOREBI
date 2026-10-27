# RRCT v0.54 Formulaic Workspace-Emergence Scale

## Operational event

A run counts as a fully emergent workspace only when all four conditions hold:

\[
A_{\mathrm{task}}\ge 0.98,
\qquad
A_{\mathrm{probe}}\ge 0.95,
\qquad
A_{\mathrm{patch}}\ge 0.95,
\qquad
A_{\mathrm{cut}}\le 0.15.
\]

This prevents ordinary task learning from being mislabeled as workspace emergence. The local and global latent states must be linearly recoverable, causally transplantable, connected to action, and necessary under ablation.

## Empirical probability surface

The combined descriptive fit is

\[
P(E=1\mid D,H,S)=\sigma\!\left(\eta(D,H,S)\right),
\]

with

\[
\eta(D,H,S)
=
-34.38224
+2.86794\log_2S
+1.23898\log_2H
+0.001565(\log_2H)^2
+2.97361\log_2D.
\]

Here:

- \(D\) is workspace bottleneck dimension;
- \(H\) is hidden width;
- \(S\) is the number of terminal-only training updates;
- \(E\) denotes full causal workspace emergence.

The corresponding single-seed threshold is

\[
S_p(D,H)
=
2^{\frac{
\operatorname{logit}(p)+34.38224
-1.23898\log_2H
-0.001565(\log_2H)^2
-2.97361\log_2D
}{2.86794}}.
\]

This is a post-hoc empirical description of one architecture and task. It is not a universal cognitive scaling law.

## Interpretation of coefficients

Within the fitted domain:

- doubling training steps adds approximately \(2.868\) to emergence log-odds;
- doubling bottleneck dimension adds approximately \(2.974\);
- doubling hidden width adds approximately \(1.24\), with a very small width-curvature term.

Thus, in this task, moderate representational slack had roughly the same fitted log-odds effect as doubling optimization time, while extra hidden width had a smaller effect.

## Estimated thresholds

| Bottleneck | Width | 50% single-seed | 90% single-seed | 95% probability all four seeds emerge |
|---:|---:|---:|---:|---:|
| 2 | 32 | 439 | 747 | 1256 |
| 4 | 16 | 290 | 493 | 829 |
| 2 | 8 | 804 | 1367 | 2300 |
| 4 | 8 | 392 | 666 | 1121 |

For an all-seed target reliability \(q\) over \(n\) conditionally independent seeds, the per-seed target is

\[
p=q^{1/n}.
\]

Substitute this \(p\) into \(S_p(D,H)\).

## What the fresh holdout showed

The development formula ranked the fresh configurations well:

\[
\mathrm{AUC}=0.900.
\]

But it was overconfident near the two-dimensional frontier:

- \(D=2,H=32,S=400\): 2 of 4 seeds emerged, not the frozen minimum 3 of 4;
- \(D=2,H=32,S=800\): 3 of 4 emerged, not 4 of 4;
- \(D=2,H=32,S=1200\), added post hoc: 4 of 4 emerged.

The failed frozen thresholds remain failed. The 1200-step point is a post-outcome boundary extension, not a retroactive holdout pass.

## Structural dimension boundary

The one-dimensional bottleneck never emerged, even at 2400 updates and approximately 2.248 billion parameter-sample products. Its mean action, probe, and transplant accuracies remained near 8%.

The target state is circular. A smooth globally faithful circle representation naturally requires at least two coordinates. This is consistent with the observed boundary, but the experiment is not a theorem excluding every discontinuous one-dimensional code.

## Uncertainty

Each frozen configuration contains only four seeds. Exact 95% binomial intervals are therefore broad. For example:

- 2 of 4 corresponds to an interval of approximately \([0.068,0.932]\);
- 3 of 4 corresponds to approximately \([0.194,0.994]\);
- 4 of 4 corresponds to approximately \([0.398,1]\).

The formula should therefore be used as:

1. an ordering of configurations;
2. an interpolation heuristic;
3. a way to nominate new frozen points.

It should not be treated as a precise universal probability forecast.

## Strongest conclusion

> Within a supplied two-level hierarchy, terminal-only training exhibits a phase-transition-like, seed-dependent onset of causally modular workspace semantics. The frontier shifts earlier with representational dimension, width, and optimization scale, but near-frontier cohort reliability is substantially more uncertain than a simple logistic fit suggests.
