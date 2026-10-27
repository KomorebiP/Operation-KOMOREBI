# V0.2 research specification

## Question

Can a global learned positive-definite latent metric plus an independently
encoded anonymous composition law produce a nondegenerate, causally usable, and
transportable recurrent operator workspace on operator tables excluded from
training?

## Task

Each episode supplies two full eight-state permutation tables, a start state,
and an anonymous operator word. Training uses D4 words of lengths 1–4. Both
exposed tables must belong to the frozen train partition. Primary evaluation
uses only base tables in the disjoint test partition and examines D4, C8, and
independent random-permutation families through depth 129.

The architecture has an explicit matrix-valued operator code and therefore
contains a strong positive inductive bias. The experiment tests execution and
closure under that bias, not spontaneous operator discovery.

## Mechanisms

For a bounded symmetric trace-free log metric S,

\[
G=\exp(S),\qquad Q(M)=\exp(S/2)M\exp(-S/2).
\]

The intrinsic isometry loss penalizes

\[
\|Q(M)^\top Q(M)-I\|_F^2/d^2.
\]

With row-coded tables, applying P then Q yields \(T_PT_Q\). Latent column maps
must satisfy

\[
E(T_PT_Q)\approx E(T_Q)E(T_P).
\]

The target table is independently encoded, stop-gradient bounded, and never
receives canonical identities or named relations.

## Primary hypotheses

1. The joint arm retains high endpoint accuracy through depth 128 on held-out
   tables and transfers to C8 and random permutations.
2. Operators are locally near-isometric and recurrent norms neither explode nor
   vanish.
3. Independently encoded composed operators agree with sequential execution and
   beat a shuffled-target null.
4. A latent state patched across distinct operator contexts controls the
   predicted continuation and beats an on-manifold wrong-state control.
5. Cross-seed affine transport beats shuffled and random maps while preserving
   operator behavior and learned metric structure.

The 26 exact gates are frozen in `protocols/V0_2_PRIMARY.json`.

## Outcome

Hypotheses 1 and 5 largely passed. Correct composition targets also clearly beat
the shuffled null. Hypothesis 2 failed because norms vanished at depth 128;
hypothesis 3 failed its absolute closure criteria; and hypothesis 4 failed its
absolute cross-context criteria. The conjunctive primary result is failure.

## Statistical unit

The primary unit is an independent training seed (n=10), not an evaluation
episode. Evaluation episode counts reduce measurement noise within a trained
model but do not inflate the number of independent model samples. Five disjoint
seed pairs form the transport sample.

