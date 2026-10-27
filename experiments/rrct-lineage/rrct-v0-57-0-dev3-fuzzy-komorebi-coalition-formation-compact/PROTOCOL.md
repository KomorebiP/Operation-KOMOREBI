# RRCT v0.57 Fuzzy Komorebi Coalition Formation Protocol

## Scientific question

Can learned fuzzy matrices provide a causally meaningful intermediate geometry between hard coalition graphs and continuously overlapping workspaces?

The primary hypothesis is:

> A terminally trained controller can infer graded workspace memberships from an anonymous noisy task-demand cue. Crisp tasks should induce relatively sharper, more projector-like packet operators, while overlap tasks should retain calibrated non-idempotence. Hard assignment should be exact on crisp tasks but fail graded tasks. A direct-edge attention model may remain predictively competitive, so the experiment tests the value of graded relational structure rather than presupposing unique superiority of the Komorebi factorization.

## Fuzzy packet construction

For four agents and three candidate shared workspaces, the controller produces a row-stochastic membership matrix

\[
U\in[0,1]^{4\times4},
\qquad
\sum_k U_{ik}=1.
\]

Packet zero is the private residual. Packets one through three are shared workspaces. The packet operators are

\[
E_k=\operatorname{diag}(U_{:k}).
\]

They satisfy

\[
E_k\succeq0,
\qquad
\sum_k E_k=I,
\]

but generally not

\[
E_k^2=E_k.
\]

The idempotence defect is therefore a direct measure of fuzziness.

For any operator \(T\), completeness gives the exact fuzzy block decomposition

\[
T=\sum_{i,j}E_iTE_j.
\]

The protocol verifies partition completeness, positivity, block reconstruction, and covariance under an agent permutation.

## Task dynamics

Each workspace has a fixed gain. Membership induces a graded coupling matrix

\[
C(U)=\sum_{k=1}^3 g_k U_{:k}U_{:k}^{\top},
\]

with the diagonal removed. Terminal actions are

\[
y=\tanh(x+\beta C(U)x).
\]

The runtime receives only:

- private agent values \(x\)
- a noisy anonymous random projection of the task membership demand
- terminal target actions during training

It does not receive:

- family labels
- membership labels
- coalition labels
- hard route labels
- evaluator correctness labels at inference

## Families

1. Crisp local and pairwise coalitions
2. Familiar fuzzy blends seen outside the central coefficient interval
3. Diffuse random fuzzy memberships
4. Held-out central interpolation blends using coefficients unseen during training

The held-out blends use familiar topology pairs but unseen coefficient values. This is a continuous interpolation test, not an unseen-topology test.

## Matched models

- **Fuzzy packet model:** predicts row-stochastic memberships and uses the induced fuzzy packet coupling.
- **Hard packet model:** same architecture but straight-through one-hot memberships.
- **Direct-edge model:** predicts six unconstrained fuzzy edge strengths without a packet factorization.
- **Oracle hard control:** crispifies the true membership matrix, isolating the representational limitation of hard assignments.

A separately labeled crystallization-pressure analysis may be run after the primary result. It is exploratory and is not part of the frozen endpoints.

## Causal tests

- Set one predicted agent-workspace membership to zero and transfer its mass to the private packet.
- Measure the increase in terminal loss.
- Correlate predicted membership strength with causal ablation effect.
- Harden the predicted fuzzy memberships and measure the resulting error on overlap tasks.
- Verify that the isolated private routine route remains intact.

## Holdout

Eight untouched seeds are fixed in `validation/HOLDOUT_SEED_SELECTION.json`.

Each seed trains fuzzy, hard, and direct-edge models with identical cue networks, hidden width, batch size, update count, and data stream family. Evaluation uses 24,000 independent holdout cases.

## Interpretation boundary

A positive result would establish, in this bounded synthetic setting, that:

- graded coalition structure can be learned from terminal behavior;
- fuzzy packets are exact operator partitions even when non-idempotent;
- task-relevant fuzziness is causally load-bearing;
- crisp and overlapping demands produce distinguishable packet geometry;
- unrestricted fuzzy edges are an important alternative explanation.

It would not establish:

- that fuzzy Komorebi packets are uniquely optimal;
- spontaneous discovery of the number of packets;
- open-world coalition formation;
- biological brain implementation;
- functional awareness, subjective experience, consciousness, sentience, or valence.
