# Claims and Limits

Version 0.1.1

## Scope

This ledger prevents exact algebra, conditional mathematics, and empirical interpretation from being blended into a single claim. It applies to the Komorebi Recurrent-Depth Lab and its analysis of Geiping et al., [*Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach*](https://arxiv.org/html/2502.05171v2).

## A. Exact statements

The following statements are exact once their explicitly stated objects exist.

1. **Repeated-core dynamics:** For a fixed embedded input and a complete state, the model defines an iteration \(s_{i+1}=T_e(s_i)\). The paper's baseline construction is given in [Section 3](https://arxiv.org/html/2502.05171v2#S3).
2. **Packet path identity:** Pairwise-annihilating idempotents summing to the identity give an exact path expansion of every finite operator power.
3. **Compressed path identity:** Packets resolving a finite feature space give an exact expansion of the compressed operator power \(A^r\).
4. **Leakage identity:** The difference between \(U^r\) and \((QUQ)^r\) has the exact telescoping form stated in `THEOREM_OUTLINE.md`.
5. **Exterior-memory identity:** With the four operator blocks \(A,B,L,D\), projected evolution obeys the exact return-memory recurrence stated in `THEOREM_OUTLINE.md`.
6. **Tangent path identity:** The chain rule and resolutions of the tangent-space identity give an exact path expansion of the derivative cocycle.
7. **Contraction tail bound:** If a complete invariant region and a contraction constant \(\kappa<1\) are proved, the state, logit, KL, and argmax bounds in `THEOREM_OUTLINE.md` follow.
8. **Cyclic phase packets:** Once cache contents and \(i\bmod k\) are included in the state, phase indicators form exact residue packets for the augmented autonomous system.

These exact statements do not depend on PCA plots, semantic labels, or benchmark performance.

## B. Exact only under additional hypotheses

| Statement | Required hypothesis | What fails without it |
|---|---|---|
| Finite Koopman model equals true evolution | The learned feature space is Koopman invariant | \(A^r\) describes repeated projection, not the true projected orbit |
| Packet energies add | Projectors are orthogonal in a specified Hilbert inner product | Oblique or overlapping packets can have interference and poor conditioning |
| Sparse graph gives an exact path grammar | Every omitted block is exactly zero | Thresholding produces a grammar residual |
| Fixed-point stopping is certified | A trapping region and uniform \(\kappa<1\) bound are proved | Successive changes can become small and later grow or rotate |
| Periodic stopping is certified | A phase-conditioned contraction for \(T^q\) is proved | A projected loop need not be a stable cycle |
| Recurrence is a refinement tower | Nested packet identities and compatible transfers are verified | Depth remains iteration count, not resolution level |
| Cross-prompt Koopman operator is autonomous | The prompt embedding is retained in a skew-product state | Different prompts define different maps \(T_e\) |
| Cache-aware Koopman operator is autonomous | Cache values, update state, and cyclic phase are included | The observed latent state follows a nonautonomous process with hidden memory |

## C. Empirical hypotheses tested by the lab

These are hypotheses, not current conclusions.

1. A low-dimensional or finite feature lift predicts held-out recurrent trajectories better than rank-matched controls.
2. The fitted feature space has small closure leakage over the tested depth range.
3. Stable packet systems recur across prompts, initialization seeds, checkpoints, and feature ranks.
4. A sparse subset of packet paths accounts for a substantial fraction of output-relevant transport.
5. Packet-path sensitivity predicts the effect of small latent interventions.
6. Fixed-point, periodic, quasiperiodic, and drift regimes can be distinguished in the full latent space.
7. Some recurrent modes align with task structure after controlling for token identity, prompt family, and trajectory depth.
8. Verified contraction certificates can stop selected trajectories safely and more informatively than successive-output KL alone.
9. Cyclic cache phase creates a genuine residue-lane structure in the augmented state, with measurable loss when cache contents are projected away.
10. Nested packet families satisfy the identities required for a Komorebi refinement interpretation.

Positive exploratory results must be repeated on held-out prompts. Time points and tokens from one prompt are correlated and must not be treated as independent experimental units.

## D. What the source paper reports

The source paper reports:

- a shared recurrent block unrolled to variable depth
- performance changes as recurrence depth changes
- a successive-output KL heuristic for per-token adaptive compute
- cyclic KV-cache reuse using recurrence index modulo a cache budget
- qualitative PCA views described as convergent paths, orbits, and sliders
- qualitatively similar dynamical patterns after changing the random initial state

The relevant primary-source sections are [Section 6](https://arxiv.org/html/2502.05171v2#S6) and [Section 7](https://arxiv.org/html/2502.05171v2#S7).

Those observations motivate this lab. They do not establish the stronger mathematical claims listed below.

## E. Unsupported claims

The current theory and planned experiments do **not** establish any of the following:

1. The model has learned a discrete, human-readable latent chain of thought.
2. PCA loops are true periodic orbits in the original latent space.
3. A complex Jacobian eigenvalue proves orbital computation.
4. Directional drift proves a Jordan block or an internal counter.
5. Similar plots from several initializations prove a unique global attractor.
6. Initialization robustness is the same concept as Komorebi chart holonomy or path independence.
7. A low EDMD training residual proves an invariant Koopman subspace.
8. Packet correlations with task labels prove causal computational roles.
9. Recurrence depth is automatically a multiscale or polyphase refinement coordinate.
10. Small KL divergence between successive outputs certifies closeness to a limiting output.
11. A finite compression \(A=QUQ\) is automatically a Koopman operator.
12. The observed dynamics demonstrate Neuralese, consciousness, awareness, or subjective reasoning.
13. Improved benchmark accuracy proves that a particular orbit, slider, or packet caused the improvement.
14. The packet path identity, Koopman lift, tangent cocycle, or contraction theorem is new mathematics by itself.
15. Structural resemblance between the paper and Komorebi Math independently validates broader Komorebi universality claims.

## F. Required controls

Every empirical claim should be compared against controls chosen before inspecting the held-out result:

- shuffled recurrence order
- shuffled prompt or task labels
- random orthogonal charts of matched dimension
- rank-matched affine and linear dynamical models
- different feature dictionaries and retained ranks
- multiple initial-state seeds
- prompt-level train, validation, and test splits
- intervention magnitudes approaching zero
- original-space recurrence tests in addition to PCA charts
- cache-aware and cache-omitted models when cyclic caching is studied

The analysis must keep these residuals distinct:

1. feature projection error
2. Koopman closure leakage
3. block-thresholding or grammar error
4. finite-sample estimation error
5. numerical floating-point error
6. nonlinear remainder in tangent interventions

Combining them into one reconstruction score would conceal the reason a model succeeds or fails.

## G. Interpretation ladder

Results should be described at the strongest level actually supported:

1. **Visualization:** a pattern appears in a chosen chart.
2. **Geometric replication:** the pattern survives different charts, seeds, and prompts.
3. **Dynamical identification:** a full-space fixed-point, return, drift, or cocycle test passes.
4. **Finite closure:** a held-out feature lift predicts multistep dynamics with quantified leakage.
5. **Packet transport:** exact packet algebra reconstructs the fitted operator and remains stable across replications.
6. **Causal lane:** packet interventions have the predicted downstream effect.
7. **Refinement system:** nested packet and transfer compatibility identities pass.
8. **Certified computation:** verified bounds support a stopping, compression, or error guarantee.

Only levels 6 through 8 would support a strong claim that the recurrent model realizes a substantive Komorebi computational structure. Lower levels remain valuable, but should be labeled exploratory or descriptive.

## H. Novelty boundary

Koopman lifting, block-operator decompositions, tangent cocycles, Floquet analysis, and Banach contraction bounds are established tools. The potential contribution of this project is their disciplined integration with Komorebi packet and refinement machinery, together with reproducible tests of learned recurrent computation.

The strongest defensible outcome would not be that every recurrent network is Komorebi by definition. It would be that a particular recurrent model admits a compact, stable, low-leakage, causally validated packet representation that yields a practical certificate or computational advantage.
