# Additional formal results for v0.2

## Partition-refinement invariance

Let \(\mathcal J=\{J_b\}_{b=1}^B\) be a partition of the variant indices and
let \(\mathcal J'\) be any refinement. Then

\[
\sum_{J\in\mathcal J}A_JA_J^\top
=
\sum_{J'\in\mathcal J'}A_{J'}A_{J'}^\top
=
AA^\top.
\]

Thus block size and block boundaries are execution parameters, not model
parameters.

The same is true for streamed actions:

\[
\sum_{J\in\mathcal J}G_JW_JG_J^\top U
=
\sum_{J'\in\mathcal J'}G_{J'}W_{J'}G_{J'}^\top U.
\]

Any permutation of variants, with weights permuted identically, also leaves
the operator unchanged.

## Hierarchical blocking theorem

Suppose a coarse block \(J\) is decomposed into disjoint children
\(J=J_1\sqcup\cdots\sqcup J_q\). Then

\[
A_JA_J^\top
=
\sum_{\ell=1}^q A_{J_\ell}A_{J_\ell}^\top.
\]

Therefore a runtime may recursively split a block that exceeds available
device memory without changing the exact operator.

This gives an exact adaptive-memory scheduler: if a block allocation fails,
halve or otherwise refine the block and continue.

## Backing-store theorem

All streaming identities depend only on sequential access to the required
tiles \(G_{I,J}\). The genotype matrix may therefore reside in host RAM,
memory-mapped storage, compressed backing storage with exact decode, or a
remote shard, provided each requested tile is reconstructed exactly before
multiplication.

The mathematical operator is independent of the backing-store location.

## Exact phase graph and PSD construction

For a factor \(A\) and phase projectors \(P_h\), the operator
\(H=A^\top A\) is PSD. If \(P_hHP_g=0\) whenever graph distance exceeds one,
then

\[
P_hH^kP_g=0
\quad\text{whenever}\quad
\operatorname{dist}(g,h)>k.
\]

This is the exact polyphase light-cone statement specialized directly to a
factor Gram operator.

## Commuting decomposition principle

Storage blocking and phase decomposition operate on different index
structures:

- storage blocking subdivides data for execution;
- phase decomposition groups coordinates for structural propagation.

Refining storage blocks inside a phase does not change the phase graph,
because the summed phase operator is unchanged.

Therefore storage refinement commutes with exact polyphase scheduling.

## Spectral-core composition

If a Krylov/range basis \(Q_r\) captures \(\operatorname{range}(A)\), then

\[
A=Q_rB,
\qquad
K=Q_rBB^\top Q_r^\top.
\]

All preceding streaming identities may be used to construct the actions that
produce \(Q_r\) and \(B\). Once the core is captured, the large backing data
is no longer needed for eigendecomposition.

This separates the computation into:

\[
\text{streamed data phase}
\to
\text{small spectral-core phase}
\to
\text{K-COS tail phase}.
\]
