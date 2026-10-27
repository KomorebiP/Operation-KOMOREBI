# RRCT v0.54 Workspace-Emergence Scaling Result Report

## Result classification

The campaign produced a **partial confirmatory success and a useful falsification**.

The qualitative scaling hypothesis passed:

- insufficient bottleneck dimension blocks emergence;
- emergence rate increases monotonically with training scale;
- larger bottleneck dimension shifts the frontier earlier;
- when emergence occurs, the latent state is probe-decodable, causally transplantable, planner-relevant, and ablation-sensitive.

The exact pre-holdout d2 reliability thresholds failed. The scaling surface ranked the tested points reasonably well, but underestimated across-seed variance.

## Why this is not merely learning-curve accuracy

The emergence criterion requires four simultaneous properties:

\[
A_{\text{task}}\ge .98,
\]

\[
A_{\text{probe}}\ge .95,
\]

\[
A_{\text{patch}}\ge .95,
\]

\[
A_{\text{cut}}\le .15.
\]

Task accuracy alone therefore cannot qualify a point. The hidden local and global states must expose the intended circular variables under frozen linear probes, control counterfactual downstream behavior when transplanted, and remain necessary under ablation.

## Structural capacity boundary

The one-dimensional system had:

- mean action accuracy .0834;
- mean probe accuracy .0800;
- mean transplant accuracy .0810;
- zero emergent seeds;
- 2.248 billion parameter-sample updates.

The task requires a continuous representation of circular state. A smooth globally faithful representation naturally requires at least two coordinates. The empirical result is consistent with that topology, though it is not a formal impossibility theorem for every conceivable discontinuous encoder.

## Phase-transition behavior

Near the frontier, seeds did not improve smoothly and uniformly. They split into qualitatively different outcomes:

- failed latent organization;
- partially decodable but insufficient workspace;
- nearly solved state;
- fully causal workspace.

Above the frontier, all three measures rapidly saturated near one while cut performance remained near chance.

This is why the result is better described as a probabilistic phase boundary than as a deterministic update count.

## Dimension effect

The frozen four-dimensional, width-16 model achieved 4/4 emergence at 400 updates using approximately 203.6 million parameter-sample products.

The two-dimensional, width-32 model required the post-hoc 1200-step point to achieve 4/4, using approximately 761.2 million parameter-sample products.

For these matched fresh seeds, the overcomplete four-dimensional representation reached reliable emergence with roughly 3.7 times less measured parameter-sample compute.

This does not establish that four dimensions are universally optimal. It establishes that modest representational slack substantially improved optimization reliability in this task.

## Frozen failures retained

Three of sixteen frozen endpoints failed:

- d2/width32/400 reached 2/4, not the required 3/4;
- d2/width32/800 reached 3/4, not 4/4;
- the pooled above-frontier mean action threshold of .99 failed because one d2 seed remained at .872.

The frozen status remains `V054_HOLDOUT_ENDPOINTS_NOT_MET`.

## Claim boundary

The coordinate semantics emerged inside a hierarchy whose topology, coalition membership, update order, tensor-product primitives, and terminal action structure were supplied. The experiment maps the scale of representation emergence, not spontaneous architecture discovery.
