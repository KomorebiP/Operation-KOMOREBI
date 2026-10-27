# V0.2 integrated findings

## Outcome

The prospectively frozen primary hypothesis **failed overall**: 20 of 26 gates
passed and 6 failed. The result is nevertheless a substantial advance over
v0.1.1 because the individual operator tables used for primary evaluation were
exactly excluded from training, ten independent optimization seeds were run,
and the strongest claims were tested against matched structural and transport
controls.

The central finding is mixed:

> A learned metric plus correct anonymous composition pressure greatly improved
> long-depth table execution and produced locally near-isometric held-out
> operators, but the recurrent state still contracted toward zero, absolute
> algebraic closure remained incomplete, and cross-context state transport did
> not reach the frozen threshold.

This supports a stable *classification computation over a finite horizon*, not
a nondegenerate invariant latent geometry.

## Exact design corrections

The v0.1.1 audit found that all 10,080 slot-ordered D4 generator-table pairs had
appeared during training. V0.2 partitions all \(8! = 40{,}320\) permutation maps
by an immutable SHA-256 hash rank:

| Split | Maps |
|---|---:|
| Train | 24,192 |
| Development | 8,064 |
| Test | 8,064 |

The exhaustive split digest is
`3aceaac6852f88360de0851eefc43bf46331d3b4efe3a04d0f2b9dfeff455340`.
Pairwise intersections are zero. Both exposed base operators in every episode
must belong to the requested split.

The primary protocol was frozen before the test split was opened. It used:

- 8 arms and 10 independent seeds, giving 80 complete arm-seed cells
- training lengths 1–4 and held-out depths 7–9, 31–33, 63–65, and 127–129
- a learned determinant-one SPD metric
- independently encoded anonymous composition targets
- a matched shuffled-target null
- cross-context state patches with on-manifold wrong-state controls
- five balanced nonzero-depth cross-seed transport pairs

## Development failure retained

The first development-only composition formulation collapsed all operator codes
toward zero. Its terminal loss remained at chance, and true and shuffled targets
were indistinguishable. That negative result is preserved under
`results/v0.2.0/smoke_noninferential`.

Before any test evaluation, the composition loss was amended to use a
stop-gradient moving target and a bounded `log1p` relative residual. Two further
development-only calibrations selected metric weight 3.0 and composition weight
0.3. No code, weights, seeds, or thresholds changed after the primary protocol
was written.

## Primary behavioral results

Means are across ten optimization seeds.

| Arm | D4 depth 8 | D4 depth 64 | D4 depth 128 | C8 depth 64 | Random depth 64 |
|---|---:|---:|---:|---:|---:|
| Terminal only | 0.9348 | 0.3402 | 0.2723 | 0.1988 | 0.1383 |
| Named relation, weight 0.60 | 1.0000 | 0.8301 | 0.5922 | 0.5699 | 0.2391 |
| Fixed Euclidean metric | 1.0000 | 0.7039 | 0.4359 | 0.3461 | 0.2453 |
| Learned metric | 0.9977 | 0.5465 | 0.3977 | 0.2543 | 0.2188 |
| Anonymous composition | 0.9973 | 0.6797 | 0.3984 | 0.4477 | 0.2344 |
| **Learned metric + composition** | **0.9879** | **0.8660** | **0.6105** | **0.7203** | **0.2273** |
| Shuffled composition null | 0.9844 | 0.6078 | 0.3871 | 0.3078 | 0.2133 |
| GRU terminal | 0.4152 | 0.3086 | 0.2758 | 0.2051 | 0.1422 |

The joint arm also remained strong at neighboring D4 depths: 0.6090 at 127,
0.6105 at 128, and 0.5750 at 129. The result is therefore not an artifact of a
single periodic endpoint.

Paired descriptive bootstrap intervals across the ten matched seeds were:

| Comparison | Mean paired difference | 95% bootstrap interval |
|---|---:|---:|
| Joint − shuffled, D4 depth 64 | +0.2582 | [0.1648, 0.3457] |
| Joint − shuffled, D4 depth 128 | +0.2234 | [0.1418, 0.2957] |
| Joint − shuffled, C8 depth 64 | +0.4125 | [0.2859, 0.5258] |
| Joint − terminal, D4 depth 128 | +0.3383 | [0.2602, 0.4133] |
| Joint − named relation, D4 depth 128 | +0.0184 | [-0.0750, 0.1258] |

The correct anonymous target therefore mattered relative to its shuffled null,
but the joint arm did not clearly outperform the named-relation comparator at
depth 128.

## Geometry and the decisive failure

Held-out operators in the joint arm appeared locally well controlled:

| Metric | Mean |
|---|---:|
| P95 spectral radius | 0.9924 |
| P95 largest whitened singular value | 1.0115 |
| P95 normalized \(G\)-isometry defect | 0.2128 |
| Learned metric condition number | 6.4119 |
| Finite trajectory fraction at depth 128 | 1.0000 |
| P95 transient \(G\)-norm gain at depth 128 | 1.0161 |

However, the median endpoint-to-start \(G\)-norm ratio at depth 128 was only

\[
0.001281.
\]

Every seed missed the frozen lower bound of 0.1. Small per-step contractions
therefore compound into a nearly vanishing state even though no transient
explosion occurs. Classification remains possible because the decoder can use
direction and small margins for a finite time, but this is not dynamical
closure in the intended norm-preserving sense.

## Anonymous composition

Correct composition pressure produced a real relative benefit:

- shuffled-minus-correct metric closure residual: +0.1222 in all 10 seed pairs
- joint-minus-shuffled D4 depth-64 accuracy: +0.2582
- joint-minus-shuffled D4 depth-128 accuracy: +0.2234

But the absolute closure gates failed:

| Test | Result | Gate |
|---|---:|---:|
| Direct composed-table substitution | 0.8750 | ≥ 0.9000 |
| Sequential/direct output agreement | 0.6617 | ≥ 0.8000 |
| Median intrinsic operator residual | 0.7797 | ≤ 0.6000 |

Thus the auxiliary teaches useful structured regularization without producing
an exact latent homomorphism.

## Cross-context state patching

The joint arm achieved:

| Test | Accuracy |
|---|---:|
| Recipient native continuation | 0.5734 |
| Re-encoded discrete-state continuation | 0.5703 |
| Cross-context latent patch | 0.4146 |
| On-manifold wrong-state control | 0.0805 |
| Patch margin | 0.3342 |

The patch is highly informative relative to the wrong-state control, but it is
not fully context-independent and missed the frozen 0.70 accuracy and 0.50
margin gates. Part of the ceiling is the model's imperfect random-family native
accuracy, but the absolute gate remains failed.

## Cross-seed transport

Five independent source-target pairs produced:

| Test | Mean |
|---|---:|
| Affine aligned continuation | 0.9848 |
| Shuffled-pair affine control | 0.1406 |
| Random-map control | 0.0809 |
| Operator-intertwining behavioral agreement | 0.9820 |
| Held-out hidden \(R^2\) | 0.6709 |
| Metric pullback defect | 0.4683 |
| Decode source label → target re-embed | 0.9922 |

Transport is real relative to shuffled and random affine maps. However, the
discrete decode–re-embed baseline was 0.0074 better on average and won or tied
all five pairs. The result therefore does not establish a richer shared latent
semantics beyond transport of the eight-state codebook. The stronger claim
would require transport of residual structure after conditioning on decoded
state identity, or a task whose hidden state contains independently variable
attributes not recoverable through one label.

## Gate ledger

Twenty gates passed and six failed. The failed gates were:

1. nonvanishing depth-128 endpoint norm
2. absolute composition substitution accuracy
3. sequential/direct composition agreement
4. absolute intrinsic closure residual
5. cross-context patch accuracy
6. cross-context patch margin

Because the protocol was conjunctive, the primary hypothesis failed.

## Reproducibility

The complete `metric_composition`, seed-200 cell was independently retrained and
reevaluated after the primary run. Every parameter was bit-identical
(`max_abs_difference = 0.0`) and every recorded metric was exactly identical.

## Calibrated conclusion

The evidence supports:

> Under an explicit matrix-operator inductive bias and exact held-out operator
> tables, learned metric plus correct anonymous-composition pressure can greatly
> extend finite-horizon recurrent execution, improve transfer to unseen cycle
> systems, suppress explosive transients, and create behaviorally transportable
> cross-seed state coordinates.

It does not support:

- nondegenerate norm-preserving dynamical closure
- an exact latent operator algebra
- fully context-independent causal state semantics
- shared Neuralese richer than a transported discrete state codebook
- spontaneous operator discovery in an unconstrained architecture
- claims about language models, awareness, or consciousness

## Next research block

The next experiment should replace soft isometry pressure with a noncontractive,
invertible operator parameterization or an explicit lower-singular-value
constraint. It should then remove the dense length-1/full-table shortcut and use
multi-attribute states so causal patches and transport must preserve information
that cannot be reconstructed from one decoded label.
