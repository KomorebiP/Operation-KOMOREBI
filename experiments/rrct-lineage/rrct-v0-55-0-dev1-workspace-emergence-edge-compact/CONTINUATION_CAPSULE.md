# RRCT v0.55 Continuation Capsule

## Established edge

Stable workspace semantics inside the supplied hierarchy follow a two-sided frontier.

### Low edge

D=1 fails. D=2 succeeds but has a long and seed-sensitive optimization tail.

### Goldilocks plateau

D=4 through approximately D=12 gives rapid and reliable onset at matched total parameter count.

### High edge

When D grows while hidden transformation width H becomes very small, onset slows sharply. D=20,H=3 has median onset 1000 updates.

## Two-stage mechanism

1. A second independent latent direction opens.
2. Semantic decoding, causal transplant, terminal task use, and ablation necessity lock together.

The second/first singular ratio is an early warning signal with AUC 0.883 for onset within 200 updates.

## Formulae

Low-dimensional primary frontier:

\[
T_{50}(D)\approx176.77+1068.10D^{-1.966}.
\]

Full post-outcome Goldilocks description:

\[
T_{50}(D,H)
\approx
208.32+1514.56D^{-2.637}+0.02422(D/H)^{5.479}.
\]

## Next gap

The hierarchy still exists before learning begins.

The next major block should expose several possible coalition graphs, hierarchy depths, and workspace costs, then ask whether terminal objectives select:

- whether a coalition should form
- which leaves should join it
- how many levels are justified
- what workspace dimension is needed
- when the workspace should dissolve

The edge variable should then be generalized from workspace semantics to **workspace formation itself**.
