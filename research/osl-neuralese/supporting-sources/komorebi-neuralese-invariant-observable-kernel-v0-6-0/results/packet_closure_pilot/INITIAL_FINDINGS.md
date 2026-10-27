# Initial findings — ambient packet closure v0.4

- Author: `Komorebi P.`
- Study: prospective developmental fresh-seed paired 2x2
- Official execution: `PASS`
- Official assay: `FAIL`
- Formal full claim: `NOT_EVALUATED`

## Bottom line

The block separated two forms of recurrent instability that the earlier work
had conflated.

Hard orthogonal operators solved the registered **metric and switched-gain
problem**: every rollout remained finite, exhaustive length-eight switched
words were behaviorally correct, and maximum projective gain stayed within
approximately \(6.7\times10^{-6}\) of one. They did **not** solve the
**semantic closure problem**. At depth 512, the three `polar_cr` D4 accuracies
were only 0.811, 0.693, and 0.572, and one seed's null-loop packet retention
fell to 0.375.

At the same time, causal state and operator replacements remained exact across
all three seeds, while geometrically matched controls stayed below 0.15.
Therefore the learned operators are locally executable and causally meaningful,
but their long compositions do not form a sufficiently coherent global action.

The most useful scientific reading is:

> Exact isometry removes amplification, but it does not remove accumulated
> semantic phase error, relation defect, or holonomy.

The frozen assay was invalidated by one numerical-boundary disagreement in one
of twelve packet rows. The diagnosis is exact and retained; consequently all
scientific metrics below are descriptive and cannot be promoted to the
preregistered full claim.

## What was tested

The experiment used a twelve-dimensional ambient space

\[
H\cong\mathbb R^{12}=P\oplus Q,
\qquad \operatorname{rank}P=8,
\qquad \operatorname{rank}Q=4,
\]

with a fixed Euclidean metric. It crossed two operator architectures with two
objectives:

| Arm | Operator | Additional objective |
|---|---|---|
| `euclidean_supervised` | Raw matrix plus per-step normalization | None |
| `euclidean_cr` | Raw matrix plus per-step normalization | Composition + finite-path return |
| `polar_supervised` | Hard \(O(12)\) polar factor | None |
| `polar_cr` | Hard \(O(12)\) polar factor | Composition + finite-path return |

Training used D4 words of lengths one through four. Identity and \(r^2\)
terminal actions were rejected from every loss-bearing terminal episode. The
held-out packet bank, intervention banks, switched words, and depth-128/256/512
evaluation banks were materialized only after all twelve checkpoints had been
serialized and hashed.

The fresh pilot used seeds 101, 211, and 307, with matched initialization,
accepted streams, and proposal streams across the four arms within each seed.

## Descriptive arm outcomes

These are means across the three frozen seeds. Packet, margin, null, and deep
entries are deliberately conservative worst-cell or deepest-depth summaries.

| Arm | Packet | Margin p10 | D4 at 512 | Cross-family minimum | Null closure | Switched gain | Switched accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| `euclidean_supervised` | 0.669 | -0.0686 | 0.596 | 0.292 | 0.693 | 2.053 | 1.000 |
| `euclidean_cr` | 0.620 | -0.112 | 0.561 | 0.237 | 0.578 | 1.918 | 1.000 |
| `polar_supervised` | 0.912 | 0.0630 | 0.674 | 0.220 | 0.771 | 1.000 | 1.000 |
| `polar_cr` | 0.935 | 0.112 | 0.692 | 0.240 | 0.719 | 1.000 | 1.000 |

Hard polar architecture improved mean held-out packet membership by 0.279,
mean grid-minimum margin by 0.178, and mean depth-512 D4 accuracy by 0.105.
Those are developmental paired estimates, not confirmatory effects.

The CR objective had a small positive mean effect within the polar stratum on
packet membership (+0.0234), margin (+0.0492), and depth-512 D4 accuracy
(+0.0182). It was not robust across seeds and reduced the mean worst null-loop
closure by 0.0521. In particular, the paired `polar_cr - polar_supervised`
null differences were +0.156, +0.281, and -0.594. Local composition and the
tested finite return paths were therefore insufficient to impose global
closure.

The objective did strongly suppress the finite path it directly measured:
mean Feshbach-return energy fell from 0.0220 to \(1.12\times10^{-5}\) within
the polar stratum, and from 0.0474 to \(3.87\times10^{-4}\) within the raw
stratum. This sharp local success alongside poor null and long-depth closure
is evidence that controlling selected three-block return channels is not the
same as controlling the full path algebra.

## Metric stability succeeded

For `polar_cr`, the exhaustive length-eight switched-word assay gave:

| Seed | Maximum projective gain | Word accuracy | Domain defined |
|---:|---:|---:|---:|
| 101 | 1.0000054 | 1.000 | 1.000 |
| 211 | 1.0000067 | 1.000 | 1.000 |
| 307 | 1.0000049 | 1.000 | 1.000 |

The audited hard-isometry defect was approximately \(4.2\times10^{-6}\) or
smaller in aggregate. This is the intended architectural positive control:
the learned raw table encoder may be ill-conditioned, but the executed polar
factor acts nearly isometrically on the registered finite bank.

An isometry guarantees

\[
\|M_g h\|=\|h\|
\]

and prevents singular-value amplification. It does not guarantee that

\[
M_{g_2}M_{g_1}\approx M_{g_2g_1}
\]

or that two semantically equivalent paths induce the same transformation on
the behaviorally relevant quotient. That missing implication is exactly what
the long-depth and null-loop results exposed.

## Semantic closure failed at depth

The primary `polar_cr` D4 curve was:

| Depth | Seed 101 | Seed 211 | Seed 307 |
|---:|---:|---:|---:|
| 128 | 1.000 | 1.000 | 0.996 |
| 256 | 0.994 | 0.963 | 0.900 |
| 512 | 0.811 | 0.693 | 0.572 |

Every output remained finite. The failure is therefore not exploding norms,
NaNs, or an undefined projective chart. It is accumulated angular or semantic
drift on a bounded orbit.

The packet results tell the same story at shorter audited prefixes. The three
worst membership values were 0.984, 0.953, and 0.867; worst tenth-percentile
margins were 0.232, 0.117, and -0.0120. The third seed crossed the decision
boundary even though its transformations were norm-preserving.

Null words sharpen the diagnosis. If a semantic relation \(w=e\) were realized
exactly, its latent product would act trivially on the task-relevant quotient.
Instead the worst null-closure values were 0.906, 0.875, and 0.375. Repeated
application therefore accumulates nontrivial **holonomy** despite exact metric
stability.

## Causal semantics remained intact

The `polar_cr` causal gates passed for every seed:

| Intervention | Seed 101 | Seed 211 | Seed 307 |
|---|---:|---:|---:|
| State transplant | 1.000 | 1.000 | 1.000 |
| Angle-matched state control | 0.146 | 0.129 | 0.143 |
| Reachable-wrong state control | 0.000 | 0.000 | 0.000 |
| Operator replacement | 1.000 | 1.000 | 1.000 |
| Relative-conjugacy control | 0.0918 | 0.0840 | 0.0820 |
| Cross-context operator control | 0.145 | 0.145 | 0.145 |

Native accuracy, defined fraction, target distinctness, and eligible fraction
were all one. The cross-context bank selected zero concrete-table collisions
with either the original or alternate operator.

This establishes an important separation: causal operator identity can be
strong at the local transition level while the family of operators fails to
close globally under long composition.

## The ambient complement was available but unused

The rank-four complement \(Q\) was real and all geometry checks passed, but the
registered causal assay found no specific computational dependence on it.
For D4, native accuracy was 1.000 in every seed and midpoint Q ablation caused
exactly zero accuracy loss. Cross-family Q ablations were also essentially
zero and never cleared the registered specificity threshold.

The native midpoint Q-energy fractions were nonzero—approximately 0.021 to
0.035—so the negative result is not the trivial statement that every state had
exactly zero Q component. It is the stronger and more relevant statement that
removing that component did not produce a specific behavioral loss relative
to the energy- and rank-matched control.

This is not evidence that ambient dimensions are generally irrelevant. It
shows that merely providing an ambient complement—and mildly penalizing a
particular departure/propagation/return path—does not force a model to use that
complement. The learned solution remained functionally concentrated in the
anchor plane.

There is also a structural tension in the present design: a return penalty can
discourage harmful Q-mediated feedback, but if the scientific aim is to study
Q as a useful temporary workspace, the task must make a purely P-confined
solution inadequate. Otherwise the cheapest solution is simply not to leave P.

## Cross-family transfer did not survive

The zero-shot C8 and mixed-cycle curves failed their descriptive thresholds.
At depth 512, `polar_cr` accuracy ranged from 0.172 to 0.305 on C8 and from
0.447 to 0.465 on mixed-cycle. Exact isometry therefore transferred geometric
stability, not the learned D4 semantic action.

## Komorebi-math interpretation

The natural mathematical object is no longer just a metric space with bounded
operators. It is a bundle of task-relevant quotient states equipped with a
connection.

For each visible context \(x\), let \(H_x\) be its latent chart and let
\(\rho_x(g)\) be the implemented operator. Hard polar control constrains
\(\rho_x(g)\) to an isometry. Semantic closure additionally requires the map
from abstract words to transformations to be path independent on the quotient:

\[
[\rho_x(w_1)h]=[\rho_x(w_2)h]
\quad\text{whenever}\quad
w_1\equiv w_2.
\]

For two equivalent paths, define a holonomy defect

\[
\mathcal H_x(w_1,w_2)
=\rho_x(w_2)^{-1}\rho_x(w_1).
\]

Norm preservation only says \(\mathcal H_x\) is isometric. It can still rotate
a state across a decoder boundary. The next control variable should therefore
be the action of \(\mathcal H_x\) on the behavioral quotient, not merely its
operator norm.

This suggests three linked targets for the next block:

1. **Relation-complete flatness.** Sample multiple paths with the same anonymous
   induced action and directly minimize their quotient-action discrepancy,
   including long null cycles not used for endpoint training.
2. **Cocycle coherence across contexts.** Learn or audit transport maps
   \(T_{xy}\) satisfying
   \(T_{xy}\rho_x(g)\approx\rho_y(g)T_{xy}\) and triangle consistency
   \(T_{yz}T_{xy}\approx T_{xz}\).
3. **A functional ambient bundle.** Replace the fixed global P/Q split with a
   context-dependent or state-dependent anchor plane on a Grassmannian, then
   construct tasks where transverse Q motion is necessary and must return with
   the correct transported phase.

The strongest bounded scientific conclusion from this block is:

> In this explicit table-conditioned recurrent architecture, hard ambient
> isometry is sufficient to suppress registered switched amplification while
> preserving exact causal state and operator interventions, but it is not
> sufficient for seed-robust finite packet closure, long-depth semantic
> accuracy, null-relation flatness, cross-family transfer, or specific use of
> the ambient complement.

## Assay boundary

The frozen A15 contract failed in one seed-by-arm packet row because one of
21,888 suffix cases had a promoted float64 normalized margin of
\(9.01\times10^{-9}\) while the native float32 decoder chose a different class.
All other seed-by-arm A15 rows and all other assay gates passed. The protocol
correctly retained the invalidation, so the official full developmental claim
is `NOT_EVALUATED` and this document labels the scientific outputs as
descriptive.

See `POSTHOC_ASSAY_DIAGNOSIS.md` and `A15_DIAGNOSIS.json` for the exact replayed
case. No threshold, seed, checkpoint, validator, or result was changed after
inspection.
