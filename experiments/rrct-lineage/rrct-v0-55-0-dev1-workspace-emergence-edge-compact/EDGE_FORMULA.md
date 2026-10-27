# RRCT v0.55 Formulaic Workspace Edge

## Operational event

A workspace is counted only when terminal task behavior, linear semantic access, causal transplant, and ablation necessity are simultaneously present.

\[
E_t
=
\mathbf 1\left[
A_{task}\ge0.98,
A_{probe}\ge0.95,
A_{patch}\ge0.95,
A_{cut}\le0.15
\right].
\]

Stable onset is:

\[
T_E
=
\min\{t:E_s=1\text{ for every recorded }s\ge t\}.
\]

## First edge: representational insufficiency

The hidden state is circular. D=1 produced no stable workspace in 12 fresh trajectories through 2400 updates.

For D=2 through D=8 at approximately matched parameter count:

\[
T_{50}(D)
\approx
T_\infty+AD^{-\alpha},
\]

where:

\[
T_\infty=176.77,
\quad
A=1068.10,
\quad
\alpha=1.966.
\]

This formula fits the five primary empirical medians with RMSE 4.64 updates.

## Second edge: transformation congestion

Increasing D forces hidden width H downward under a fixed parameter budget. The full post-outcome descriptive fit is:

\[
T_{50}(D,H)
\approx
T_0
+AD^{-\alpha}
+B(D/H)^\beta,
\]

with:

\[
T_0=208.32,
\]

\[
A=1514.56,
\qquad
\alpha=2.637,
\]

\[
B=0.02422,
\qquad
\beta=5.479.
\]

Interpretation:

- \(AD^{-\alpha}\) is the low-dimensional representational penalty.
- \(B(D/H)^\beta\) is the high-dimensional transformation-congestion penalty.
- \(T_0\) is an approximate optimization floor in this architecture.

The broad minimum occurs around D=6 through D=12 in the tested matched-parameter family.

## Two-stage order parameter

Let \(Z_A,Z_B,Z_G\) be the two local and one global workspace states. Define:

\[
r_t
=
\min_{Z\in\{Z_A,Z_B,Z_G\}}
\frac{\sigma_2(Z_t)}{\sigma_1(Z_t)}.
\]

The rank-opening event is:

\[
r_t\ge0.5.
\]

A stronger empirical precursor threshold:

\[
r_t\gtrsim0.744
\]

predicts stable onset within 200 updates with AUC 0.883.

The transition is therefore approximately:

\[
\text{rank opening}
\longrightarrow
\text{semantic and causal locking}
\longrightarrow
\text{stable workspace}.
\]

## Probability edge

The preregistered dense primary analysis fit:

\[
P(T_E\le S\mid D)
=
1-\exp\left[-\left(\frac{S}{\lambda(D)}\right)^k\right],
\]

with:

\[
k=3.296.
\]

A shape greater than one indicates increasing onset hazard and a comparatively sharp transition.

## Boundary

These equations describe one synthetic, terminal-only, supplied hierarchy. They should be used as:

- interpolation within the tested architecture
- a guide for new frozen points
- a mechanistic hypothesis about rank opening and causal locking

They should not be represented as universal laws of brains, AI systems, or consciousness.
