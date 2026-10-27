# Flat Packet Connection Protocol v0.5.0

**Author:** Komorebi P.

## Question

Version 0.4 showed that hard operator isometry prevents radial explosion but
does not prevent angular drift, null-loop holonomy, or continuation-packet
erosion. Version 0.5 asks whether the missing property is semantic flatness:

> Does anonymous short-relation supervision make a hard-isometric recurrent
> operator system path-independent on long, unseen derived consequences while
> preserving noncollapsed, causally executable semantics?

Every learned arm uses the same table-conditioned
`PolarIsometricTableOperatorRNN` and therefore executes matrices in
approximately \(O(12)\). Metric stability is held fixed rather than counted as
a new result.

## Two distinct flatness targets

For a visible context \(x\), a word \(w\), its exact table action
\(\tau_x(w)\), and learned product \(\rho_x(w)\), paths are equivalent when

\[
u\equiv_xv\quad\Longleftrightarrow\quad\tau_x(u)=\tau_x(v).
\]

Full latent flatness requires

\[
H_x(u,v)=\rho_x(v)^\mathsf T\rho_x(u)=I_{12}.
\]

The normalized defect is

\[
\delta_H=\frac{\lVert H-I\rVert_F}{2\sqrt{12}}.
\]

Finite packet-quotient flatness is weaker. Let \(D\) be the decoder, \(B\)
the eight learned anchor columns, \(J=I-\mathbf1\mathbf1^\mathsf T/8\), and

\[
\psi(z)=\frac{Jz}{\lVert Jz\rVert_2}.
\]

For registered construction suffixes \(s\), it requires

\[
\psi(D\rho(s)\rho(u)B)=\psi(D\rho(s)\rho(v)B).
\]

This permits full-space holonomy that no registered continuation can observe.
The exact and quotient targets are trained and measured separately.

For the multiscale training objective, write

\[
H=\rho(v)^\mathsf T\rho(u).
\]

The packet arm controls the visible effect of \(H^k-I\) at
\(k\in\{1,2,4,8,16\}\). It does not control \(k=32\), which is reserved for
evaluation. This distinction tests whether a small one-cell discrepancy stays
behaviorally invisible when the same holonomy is accumulated repeatedly.

## Anonymous relation-complete construction cells

For each pair of visible integer tables, the trainer builds their finite
transformation Cayley graph, finds the lexicographically shortest BFS normal
form of every induced action, and compares every directed edge with the normal
form of its endpoint. D4 has sixteen directed edges and seven tree edges,
leaving nine non-tree cells.

The model sees paths and visible tables only. It receives no group name,
relation label, canonical generator alignment, conjugating permutation,
normal-form label, or proof. This is explicit anonymous relation supervision,
not spontaneous relation discovery.

Training probes are the eight BFS normal forms discovered from the visible
tables. Exact evaluation
paths have adjacent-parity lengths 8/9, 16/17, 24/25, and 32/33; evaluation
suffixes begin at length four. A fixed word-length parity can realize only four
of the eight D4 action strata, so the adjacent pairs are required for balanced
coverage rather than being optional extra depths.
Each held-out branch requires at least three non-tree reductions and is absent
from the construction cells under the registered reversal, branch-exchange,
and generator-swap symmetries.

## Matched arms

| Arm | Additional structural objective |
|---|---|
| `polar_supervised` | none |
| `polar_cr_v04` | fresh-seed v0.4 composition/return comparator |
| `polar_exact_flat` | full twelve-dimensional cell equality |
| `polar_packet_flat` | finite continuation-quotient equality |
| `polar_hybrid_flat` | exact plus packet equality |
| `polar_shuffled_packet` | deliberately false equalities with the same right-branch multiset |

All arms share initialization, accepted and rejected terminal proposals,
training length schedule, optimizer budget, and construction schedule within a
seed. Common training remains

\[
L_{terminal}+0.25L_{construction\ endpoint}+0.01L_{anchor}.
\]

Every exact-active arm uses all nine cells at every step. Exact pressure ramps
over the first 200 steps to weight 0.30. Packet pressure is absent through step
400, ramps linearly through step 800, and then has weight 0.05. Its observer
side—anchors, decoder, and suffix products—is stop-gradient, so the objective
can move the path holonomy but cannot move the measuring instrument around a
residual. With centered logits, each packet term is

\[
\frac{
\operatorname{MSE}\!\left(JD\rho(s)(H^k-I)B\right)
}{
\operatorname{stopgrad}\!\left(
\operatorname{MSE}\!\left(JD\rho(s)B\right)+10^{-4}
\right)}.
\]

Relation terms receive no endpoint labels. The inherited terminal-label firewall still
rejects identity and \(r^2\) endpoint actions, but the flatness losses expose
short same-action structure. The valid held-out claim concerns long derived
consequences, not wholly unseen defining relations.

## Post-seal assays

Checkpoints are saved and hashed before any scientific evaluation bank is
materialized. The audit includes:

- long same-histogram equivalent diamonds followed by unseen suffixes;
- length- and histogram-matched non-equivalent pairs with discriminating
  starts;
- prefix–null-loop-repeat–suffix paths against prefix–suffix baselines for
  repeats 1, 2, 4, 8, 16, and 32;
- random D4 execution at depths 128, 256, and 512;
- separately reported zero-shot C8 and mixed-cycle execution;
- hardened state and operator replacements with matched controls;
- hard-polar orthogonality and determinant checks.

The primary behavioral score is robust joint correctness of both equivalent
paths under the registered native-float margin contract, not agreement alone.
Agreement on a shared wrong or boundary answer is failure. The same robust
contract applies to long-depth and loop-plus-suffix claims. Geometry is
computed separately from explicitly promoted float64 copies of the executed
float32 operators and cannot change a behavioral label.

## Calibration controls

1. An exact compiled \(P\)-representation with identity action on \(Q\) must
   be perfectly correct and fully flat.
2. A quotient-flat oracle with deliberately relation-violating \(Q\) rotations
   must remain behaviorally perfect while retaining nonzero full holonomy.
3. A suffix-visible synthetic residue must agree immediately and diverge after
   a future probe.
4. Identity collapse must fail non-equivalent sensitivity.
5. Random orthogonal operators must pass norm stability and fail semantics.

If any calibration control behaves incorrectly, learned-model results are not
scientifically evaluated.

## Numerical contract

The native forward path is float32. Exact float32 logit bytes are hashed.
Argmax uses those logits. True-versus-best-other gaps are computed by promoting
those same stored values to float64; hidden states and weights are not
recomputed. Robust membership is

\[
\text{native argmax correct}\ \land\ \text{normalized gap}>2^{-18}.
\]

Every absolute margin at or below the threshold is a registered boundary
failure. Robust membership is therefore a subset of native correctness by
construction. Holonomy diagnostics use declared float64 casts of executed
matrices and do not determine behavioral labels.

## Outcome statuses

The runner reports four independent statuses:

- `execution_integrity`
- `assay_validity`
- `scientific_flatness`
- `scientific_connection`

Package verification succeeds for an intact, valid negative result. It does
not require the scientific hypothesis to pass. Cross-context learned
connection transport is deliberately not adjudicated in this block.

## Ambient-space separation

The ANC-4 companion calibration tests a different proposition: under an exact
rank-eight saturated semantic contract and no temporal side channel, a
continuous online delay-four task requires a four-dimensional vertical fiber
\(K=\ker\pi\). It validates whether ambient interventions can detect truly
necessary memory. It cannot rescue a failed flatness result, and nonzero
ambient energy alone is never evidence of useful ambient computation.

## Claim boundary

A pilot pass would support finite-depth, structurally supervised D4 path
independence in this explicit small architecture. It would not establish
spontaneous Neuralese, infinite-horizon flatness, universal group learning,
architecture-independent emergence, a learned cross-model connection,
awareness, or consciousness.
