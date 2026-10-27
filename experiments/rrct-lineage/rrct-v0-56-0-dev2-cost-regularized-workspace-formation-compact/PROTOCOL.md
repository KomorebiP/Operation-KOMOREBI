# RRCT v0.56 dev2 Cost-Regularized Workspace Formation Protocol

## Question

Can a learned selector decide whether to activate no workspace, one flat workspace, one of three two-level coalition graphs, or an overlapping full workspace, using terminal counterfactual performance and an explicit activation cost?

## Supplied candidate routes

1. no workspace, cost 0;
2. flat workspace, cost 1;
3. pairing `(0,1)|(2,3)`, cost 2.5;
4. pairing `(0,2)|(1,3)`, cost 2.5;
5. pairing `(0,3)|(1,2)`, cost 2.5;
6. overlapping full route, cost 4.

The route library, route computations, and public task dependency signatures are supplied. The experiment tests selection, depth, coalition membership, and dissolution over that library; it does not test invention of new graphs.

## Objective

For route `r`, episode `e`, terminal loss `L_r(e)`, and route cost `C_r`:

\[
J_r(e;\lambda)=L_r(e)+\lambda C_r.
\]

A counterfactual target distribution is computed from all candidate terminal losses:

\[
q(r\mid e)\propto\exp[-J_r(e;\lambda)/0.05].
\]

The router sees only an anonymous noisy projection of the public dependency signature. It never receives the evaluator task index or an oracle route label.

## Primary confirmation

- lambda: 0.12
- 16 fresh seeds
- 20,000 evaluation episodes per seed
- cue noise standard deviation: 0.08

## Cost edge

Six independent seeds are tested at:

`0, 0.01, 0.03, 0.05, 0.08, 0.12, 0.16, 0.20, 0.22, 0.24, 0.26, 0.30, 0.40`.

## Frozen endpoints

The primary cohort must achieve at least 99.5% task and minimal-route accuracy for every seed, exact mean-cost matching, correct no/flat/pair/overlap selection, cue-shuffle failure, route-patch effects, graph switching, and workspace dissolution. The cost sweep must show overformation at zero cost, a nonempty optimal band, first failure on the expensive overlap route, and later pair-hierarchy failure consistent with empirical break-even costs.

## Boundary

This is a bounded task-conditioned routing experiment over supplied workspace primitives. It does not establish spontaneous graph invention, brain equivalence, functional awareness, consciousness, sentience, or valence.
