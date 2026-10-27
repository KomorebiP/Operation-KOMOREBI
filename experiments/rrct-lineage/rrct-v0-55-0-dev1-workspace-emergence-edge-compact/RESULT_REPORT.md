# RRCT v0.55 Workspace-Emergence Edge Result Report

## Result status

The primary fresh-seed study passed all 14 frozen endpoints. A separately frozen, post-primary overcomplete extension passed all four of its endpoints.

The main result is a two-sided edge:

```text
D = 1
representationally insufficient
        ↓
D = 2
sufficient but long-tailed and interaction-sensitive
        ↓
D = 4–12
broad reliable Goldilocks region
        ↓
D = 16
rare delayed locking begins
        ↓
D = 20 with H = 3
transformation congestion dominates
```

## Why the result is stronger than v0.54

Version 0.54 had four seeds per configuration, independent retraining at each step count, and dimension/parameter confounding.

Version 0.55 uses:

- 24 paired fresh seeds at each D=2,3,4,6,8 point
- 12 D=1 controls
- nearly matched parameter counts
- one continuous trajectory per seed
- dense checkpoints
- stable-onset rather than instantaneous success
- crossed initialization and data-stream seeds
- a prospectively sealed high-dimensional extension

## Exact primary observations

All 12 D=1 models failed through 2400 updates.

Of 24 D=2 models, 23 stabilized by 1400. The remaining trajectory reached stable onset at 1800 in a clearly labeled post-outcome tail extension.

Every D=3, D=4, D=6, and D=8 trajectory stabilized by the primary horizon.

No successful trajectory suffered a later recorded relapse after stable onset.

In 97.5 percent of successful trajectories, task, probe, and causal-transplant threshold crossings occurred within 150 updates of one another. Median spread was 75 updates.

## Two-stage mechanism

The second singular mode of each workspace state opens well before full semantic and causal locking.

At D=2, median rank opening occurred around 162.5 updates, but full stable onset occurred around 450 updates.

At D=8, median rank opening occurred around 75 updates and full onset around 200 updates.

Representational slack therefore accelerates both:

1. creation of a sufficiently rich latent geometry
2. organization of that geometry into a causally modular computation

## D=2 stochasticity

The crossed design used eight initialization seeds and four data-stream seeds.

A two-way additive decomposition assigned:

- 32.5 percent of log-onset variation to initialization
- 1.7 percent to the data stream main effect
- 65.8 percent to interaction and residual variation

The correct interpretation is not that data order is irrelevant. Rather, no data stream is universally good or bad. Its effect depends strongly on the initial geometry.

## High-dimensional reversal

The overcomplete extension shows that dimension helps only while transformation width remains adequate.

D=10 and D=12 remain on the fast plateau.

D=14 and D=16 show early signs of slowing and longer tails.

At D=20 and H=3, median onset rises to 1000 updates and the 90th percentile reaches the 1400-update horizon.

Thus, workspace capacity and workspace manipulability are separate resources.

## Interpretation

The tested hierarchy appears to need:

- at least two smooth coordinates for the circular hidden state
- some redundant workspace capacity to make optimization reliable
- enough hidden transformation width to learn how to operate on that workspace

The edge is not a single scalar compute threshold. It is a balance among:

\[
\text{intrinsic state dimension},
\quad
\text{workspace dimension},
\quad
\text{transformation width},
\quad
\text{optimization trajectory}.
\]

## Limitations

The formula is fitted after observing the overcomplete extension. It is descriptive.

The task remains synthetic and low dimensional.

The hierarchy remains supplied.

The high-dimensional extension uses 12 seeds per point, which is substantially better than four but still leaves finite uncertainty.

No result bears directly on subjective awareness.
