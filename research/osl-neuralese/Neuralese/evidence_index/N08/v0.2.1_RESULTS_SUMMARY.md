# Neuralese Causal Completion — learned-checkpoint audit

Author: Komorebi P.  
Version: 0.2.1  
Date: 2026-09-03  
Status: adaptive developmental analysis; frozen checkpoints; no retraining

## Bottom line

The learned projective system supports a clean **finite hard-decision quotient** on ordinary reachable histories, and its short reachable-state action behaves like a faithful D4 action. It does **not** yet support a stable causal completion.

The failure is specific. One application of each D4 identity word is behaviorally silent through the registered suffix horizon, but its full projective tangent can amplify perturbations. Repeating the same identity word 16 times accumulates angular drift, erodes margins, and creates continuation-visible errors. The best description of the current object is therefore:

\[
\boxed{
\text{task-local finite semantic action}
+
\text{history-dependent microstate}
+
\text{noncontracting loop defect}
}
\]

This is stronger than a mere shallow classifier and weaker than a normally attracting, path-independent Neuralese realization.

## Registered result

The registered profile used both projective seeds, 64 post-training D4 coordinate resamples per seed, every one of the eight semantic starts, a depth-8 reachable prefix for loop and Cayley audits, exhaustive suffixes through the declared horizons, and no parameter updates.

| Gate | Result | Main observation |
|---|---:|---|
| Execution and checkpoint integrity | PASS | Exact checkpoint digests; NumPy replay discrepancy `0.0009766` at depths 1–4 and `0.0278320` at deeper backend-sensitive depths. |
| Q0 finite behavioral quotient | PASS | `61,440/61,440` continuation decisions per seed were correct for every depth-6 history and every suffix through depth 3; exactly one hard-prediction signature occurred per semantic state. |
| P1 positive-scale gauge | PASS | All registered hard predictions were invariant under positive rescaling. |
| P2 projective path flatness | FAIL | Worst repeat-16 median ray angle was `0.45636` rad; worst H8 continuation survival was `0.92969`. |
| A1 D4 Cayley action | PASS | All 64 products had current agreement `1.0` and H4 continuation survival `1.0`; every representative endpoint was correct. |
| A2 action separation | PASS | All 28 D4 element pairs had a separating witness in every audited episode. |
| N1 frozen contraction certificate | FAIL | Worst one-loop p95 full-tangent gain was `1.97956`. |
| Projective versus gauge-fixed raw parent | PASS | Mean H8 survival advantage `+0.96810`; mean angular advantage `0.53691` rad, with episode-cluster bootstrap intervals wholly above zero. |

All execution gates passed. Not all scientific gates passed.

## The decisive split: ordinary histories versus adversarial identity histories

For the projective checkpoints, every ordinary depth-6 history collapsed to the correct hard-decision continuation signature through suffix horizon 3. Same-label rays were also geometrically tight:

| Seed | Median within-label ray angle | Post-hoc centroid one-step closure | Anchor-to-centroid angle |
|---:|---:|---:|---:|
| 0 | `0.02543` | `0.01236` | `0.60166` |
| 1 | `0.03329` | `0.01579` | `0.68963` |

The centroids are episode-conditioned, label-informed, in-sample descriptive representatives. They are not a learned global chart or evidence for an architecture-independent atlas. Their value is diagnostic: raw embedding anchors are far from the recurrent history clusters, so inserting loops at the anchors would measure the transient rather than the learned recurrent codebook.

Short reachable-state algebra was exact under the hard-decision interface. All 64 Cayley products agreed with their canonical reductions through every suffix of length at most 4, and all 28 element pairs remained distinguishable.

The same closure did not survive adversarially long identity histories. At repeat 16:

| Seed | Relation | Endpoint accuracy | H8 continuation survival | Median ray angle |
|---:|---|---:|---:|---:|
| 0 | \(F^2\) | `1.0000` | `0.99805` | `0.23831` |
| 0 | \(FRFR\) | `1.0000` | `0.97461` | `0.35439` |
| 0 | \(R^4\) | `1.0000` | `0.96875` | `0.36637` |
| 1 | \(F^2\) | `1.0000` | `0.98438` | `0.31291` |
| 1 | \(FRFR\) | `0.99805` | `0.95898` | `0.45205` |
| 1 | \(R^4\) | `0.98828` | `0.92969` | `0.45636` |

One loop remained hard-decision equivalent through H8 for every registered relation and case. Its p95 full positive-ray tangent gain was nevertheless between about `1.62` and `1.98`, depending on seed and relation. The continuous defect is initially hidden inside the decision region; repetition makes it causally visible.

## Hard-decision quotient is not the full predictive quotient

The strongest theoretical definition used future output laws, not only `argmax` answers. Under that stronger interface, the eight-state collapse is not exact:

- concatenated continuation-probability signatures have nonzero within-label RMS spread: `0.00751` and `0.01129` for seeds 0 and 1;
- the centered-logit projective-tangent proxy has rank 7 by horizon 1 for every audited case, and usually already at horizon 0;
- same-label pair separation does not systematically contract under common continuations. Median depth-8 final/initial angle ratios were `1.00679` and `0.99145`.

Thus Q0 certifies a finite **hard-decision** causal quotient over the registered history/suffix window. It does not certify an exact quotient of logits, probabilities, or all future behavior. There remains a history-dependent microstate that changes confidence and eventually changes answers.

The preregistered N1 label is also stronger than what was identified. The implemented derivative is the full seven-dimensional positive-ray tangent derivative,

\[
DF_M(h)=\frac{(I-uu^{\mathsf T})M}{\lVert Mh\rVert},
\qquad
u=\frac{Mh}{\lVert Mh\rVert}.
\]

It is not a derivative restricted to a separately identified vertical fiber. Failing N1 denies the registered all-tangent contraction certificate; it does not by itself prove that every possible semantic-fiber construction is non-attracting.

## Radial mechanism: two different problems

The post-hoc numerical audit separates the original raw parents from the projective-trained checkpoints.

| Arm | Seed 0 median operator radius | Seed 1 median operator radius | Interpretation |
|---|---:|---:|---|
| Raw terminal | `1.8412` | `1.9877` | Expanding ambient realization. |
| Relation pressure | `1.2831` | `1.2446` | Reduced, but still expanding. |
| Projective terminal | `0.1988` | `0.1970` | Strongly shrinking before normalization. |

Every sampled projective-trained operator also had Euclidean 2-norm below one (maxima `0.5884` and `0.5122`). This is a finite audited-set statement, not a general joint-spectral certificate.

For these projective-trained weights, normalization prevents vanishing rather than suppressing explosion. In NumPy float32 emulation at depth 64:

- seed 0 retained nonzero states and logits in only `2.15%` of cases, while normalized accuracy was `1.0`;
- seed 1 retained none, while normalized accuracy was `1.0`.

Float64 can preserve the mathematical ray far beyond this point, but that idealized agreement is not an execution-fidelity result. Zero logits are invalid underflows, not legitimate class-zero predictions.

Normalization therefore solves the radial numerical degree of freedom in both signs: it can suppress explosion in one checkpoint family and prevent vanishing in another. It cannot remove angular loop drift.

## The quotient needs two depth axes

The result exposes a missing index in the earlier causal-refinement theory. Let \(R_{\le L}\) be states reachable by histories of length at most \(L\), and let \(\sim_H\) identify states that no continuation of length at most \(H\) can distinguish. The finite object is

\[
Q_{L,H}=R_{\le L}/\!\sim_H.
\]

Increasing \(H\) refines future discrimination. Increasing \(L\) enlarges the reachable domain and can expose new microstates even when \(H\) is fixed. A stable causal completion requires compatibility in both directions:

1. future refinement stabilizes as \(H\) grows;
2. new histories do not split an old semantic class as \(L\) grows;
3. generator actions descend consistently across both indices.

The current system passes a small ordinary-history window such as \(Q_{6,3}\), plus the registered short Cayley window, but repeat-16 relation histories show that stabilization in the past-depth direction has not occurred.

This suggests a more precise provisional object:

\[
\boxed{
\text{Neuralese candidate}
=
\{Q^{\mathrm{hard}}_{b,L,H},
Q^{\mathrm{soft}}_{b,L,H},
F_g,
P_{b\to c}}
}
\]

with explicit hard/soft observation interfaces, history depth \(L\), future horizon \(H\), context \(b\), and compatibility defects between them.

## What the next repair should target

The next intervention should not begin by fitting an unconstrained ambient metric. It should target the observed failure directly:

1. Measure the full \((L,H)\) completion surface for random histories and adversarial relation-loop histories.
2. Fit any semantic section or centroid map on one episode split and evaluate it on another; do not use in-sample centroids as an atlas certificate.
3. Identify a vertical residual only after choosing the observation interface. Hard decisions, logits, and probabilities induce different quotients.
4. Train relation closure on reachable states and repeated identity loops, not on raw embedding anchors alone.
5. Add a same-semantics shared-continuation contraction objective for the residual microstate while preserving a neutral, faithful semantic action.
6. Test whether an explicit retraction onto an episode-conditioned semantic section yields

   \[
   \pi_b\circ F_g=\rho_b(g)\circ\pi_b,
   \qquad
   \|DF_g|_{\ker d\pi_b}\|<1.
   \]

The decisive success criterion is not merely bounded norm. It is exact or controlled semantic algebra, stable extension in both depth axes, and contraction only in the genuinely behaviorally redundant directions.

## Scope and provenance

- The registered D4 coordinate draws are post-training resamples, not held-out table-pair support. Deterministic source-generator reconstruction covers all `10,080` ordered D4 table pairs and every registered probe pair. This reconstruction is not a stored-episode receipt.
- Q0 uses hard predictions and finite horizons.
- Post-hoc centroids are label-informed resubstitution diagnostics.
- Raw-terminal and relation-pressure loop comparisons use post-hoc per-step normalization and are gauge-fixed comparisons, not their original trained executions.
- The post-hoc float32 audit is a NumPy emulation, not bitwise PyTorch parity.
- No same-space quotient spectrum, invariant metric, global joint spectral radius, universal atlas, spontaneous Neuralese, architecture independence, or unbounded recurrence is claimed.

The complete machine-readable result is `results/RESULTS.json`; the numerical-mechanism supplement is `results/POSTHOC_NUMERIC_MECHANISM.json`. The failed v0.2.0 smoke and its original registration are preserved under `results/development_v0.2.0/`.
