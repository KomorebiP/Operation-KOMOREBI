# Invariant observable kernel v0.6 calibration findings

**Version:** 0.6.0  
**Author:** Komorebi P.  
**Status:** developmental calibration; screen and pilot not run

## Outcome

The v0.6 implementation and assay are operational, but the frozen scientific
experiment is stopped before the untouched screen.

The decisive result is a **positive-control calibration failure**. In the
final seed-887 implementation rehearsal, the trained hard-kernel semantic-flat
arm satisfied the registered rank, isolation, and ambient-curvature conditions,
but failed both the depth-512 behavioral threshold and the semantic-defect
thresholds. The unrestricted learned-intertwiner arm retained excellent task
accuracy and several good local residuals, but did not produce a rank-seven
observable quotient: its suffix observer remained rank twelve and injected
null directions became behaviorally visible under longer continuations.

Seed 887 was already a touched development seed. Seed 947 remains untouched.
No v0.6 screen or five-seed pilot was run, and no confirmatory claim is made.

## What was rehearsed

Two separate critical-arm rehearsals used the exact frozen screen training
recipe:

| Setting | Value |
|---|---:|
| Training steps | 3,200 |
| Batch size | 128 |
| Auxiliary contexts per step | 8 |
| Relation cells per context | 9 |
| Auxiliary delay | step 800 |
| Auxiliary ramp completion | step 1,600 |
| Simplex-Gram weight | 0.1 |
| Centered-readout weight | 1.0 |
| Intertwining weight | 10.0 |
| Semantic-relation weight | 0.3 |

The learned observer used the registered output-rowspace initialization and
the basis-free centered-simplex Gram objective. These rehearsals were
developmental checks on retired seed 887, not registered screen results.

## Learned-intertwiner result

| Quantity | Seed-887 rehearsal | Screen criterion | Reading |
|---|---:|---:|---|
| Train lengths 1--4 accuracy | 1.0000 | -- | solved |
| D4 depth 32 accuracy | 1.0000 | -- | solved |
| D4 depth 128 accuracy | 1.0000 | -- | solved |
| D4 depth 512 accuracy | 0.8203 | at least 0.7000 | locally encouraging |
| Suffix-observer rank | **12** | exactly 7 | **failed extraction** |
| \(\sigma_8/\sigma_1\) | **0.04995** | at most 0.001 | **failed extraction** |
| Principal-angle distance | 0.00635 | at most 0.10 | passed in isolation |
| Centered-readout leakage | 0.00308 | at most 0.02 | passed in isolation |
| Generator leakage, p95 / max | 0.02022 / 0.02434 | 0.05 / 0.10 | passed in isolation |
| Intertwining defect, median / p95 | 0.00757 / 0.00994 | 0.02 / 0.05 | passed in isolation |
| Semantic defect, median / p95 | 0.01730 / 0.04180 | 0.03 / 0.10 | passed in isolation |
| Null curvature, median | 0.3991 | at least 0.10 | noncollapsed |
| Length-64 leakage, median | 0.1127 | -- | substantial accumulation |
| Length-64 leakage, p95 / max | **0.3569 / 0.6556** | 0.10 / 0.20 | **failed closure** |

This is not an accuracy failure. It is a closure failure hidden beneath good
accuracy. The learned observer aligns closely with the centered readout, and
the one-generator cross blocks are small, but they are not zero. Because the
operators are orthogonal, radial explosion is absent; repeated composition
instead accumulates angular misalignment between the proposed semantic plane
and its complement. We call this **accumulating phase error** descriptively:
small per-step rotations across the proposed split compound until nominally
null directions become suffix-visible.

The rank-twelve observer is the decisive certificate. The apparent
five-dimensional null fiber is not dynamically invariant, even though the
model answers many long compositions correctly and several local residuals
fall below threshold. Accuracy and one-step intertwining are therefore not
sufficient evidence of a quotient connection.

## Hard-kernel semantic-flat result

| Quantity | Seed-887 rehearsal | Hard calibration | Reading |
|---|---:|---:|---|
| Train lengths 1--4 accuracy | 1.0000 | -- | solved |
| D4 depth 32 accuracy | 1.0000 | -- | solved |
| D4 depth 128 accuracy | 0.8555 | -- | degraded |
| D4 depth 512 accuracy | **0.3984** | at least 0.8000 | **failed** |
| Suffix-observer rank | 7 | exactly 7 | passed |
| \(\sigma_8/\sigma_1\) | \(4.11\times10^{-7}\) | at most \(5\times10^{-5}\) | passed |
| Principal-angle distance | \(4.27\times10^{-8}\) | structural | passed |
| Generator leakage, max | \(1.85\times10^{-7}\) | at most \(5\times10^{-5}\) | passed |
| Length-64 leakage, median / p95 / max | \(1.08/4.03/6.39\times10^{-6}\) | structural | passed |
| Semantic defect, median | **0.05110** | at most 0.020 | **failed** |
| Semantic defect, p95 | **0.08794** | at most 0.080 | **failed** |
| Ambient curvature, median | 1.3743 | at least 0.10 | passed |

Null-retention interventions were not measured by the lightweight rehearsal,
so they are not credited. The failures above are already sufficient to stop.

This arm establishes that the compiled split itself works: the centered
behavioral carrier is rank seven, the five-dimensional null fiber is isolated,
long products retain that isolation, and the four-dimensional ambient block
remains curved. What failed was learning a sufficiently accurate and flat
semantic action inside the protected seven-dimensional block. A perfect pipe
does not help if the transformation sent through it is wrong.

## The smoke and analytic controls

The verified forty-step smoke at
`results/invariant_kernel_smoke_v1_dev/` passed execution integrity and assay
validity. Its scientific status is correctly
`DEVELOPMENTAL_NOT_ADJUDICATED`; forty-step model performance is not used as
an efficacy result.

The analytic controls nevertheless provide an important positive result about
the assay and the ambient construction:

| Control | Key observation |
|---|---|
| Exact compiled | depth-128 robust accuracy 1.0; diamond and loop joint-robust accuracy 1.0; exact quotient flatness |
| Quotient-curved ambient | depth-128 robust accuracy 1.0; diamond and loop joint-robust accuracy 1.0; quotient defect \(3.31\times10^{-16}\) |
| Quotient-curved ambient | full/vertical path defect 0.3777 while logits match the exact control with maximum absolute delta 0 |
| Exact kernel intervention | nonzero common and ambient probes have zero centered behavioral effect through suffix length 32 |
| Cross-block-leaky negative control | rejected with cross-block leakage 0.5096 |
| Rank-collapse/intrusion controls | rank-six and rank-eight constructions correctly rejected |
| Coordinate conjugate | classification and behavior preserved under the registered global orthogonal gauge change |

These controls show that the evaluator can distinguish three cases that must
not be conflated:

1. exact quotient flatness with a flat fiber;
2. exact quotient flatness with nonzero, behaviorally inert vertical
   curvature; and
3. apparent horizontal structure contaminated by cross-block leakage.

Thus the stopped experiment is not explained by an assay incapable of
recognizing the target. The exact and quotient-curved controls realize the
target analytically. The trained positive control simply did not learn its
semantic block well enough under the frozen recipe.

### Posthoc exact-depth localization

A no-training diagnostic subsequently evaluated the analytic exact quotient
and quotient-curved controls on 128 retired-seed D4 episodes at depths 512,
4,096, and 16,384. Both controls achieved 1.0000 ordinary and robust accuracy
at every depth, with zero boundary decisions. At depth 16,384 their minimum
decision margins remained 1.06864 and 1.06856 respectively.

This diagnostic is posthoc and does not rescue or reopen v0.6. It demonstrates
the narrower mechanistic fact needed for the successor: exact quotient
functoriality eliminates the accumulated semantic drift even while the ambient
fiber remains curved. The full receipt is retained in
`results/invariant_kernel_seed887_final_rehearsal/POSTHOC_EXACT_DEPTH.json`.

## What the ambient-space formulation resolved

The ambient-space question was essential. The correct object is not merely a
small stable state vector but an exact-sequence candidate

\[
0\longrightarrow N\longrightarrow H
\xrightarrow{\Pi}\bar S\longrightarrow0,
\]

with the hard-arm flag

\[
0\subset K\subset N\subset H,
\qquad
H=S_h\oplus L\oplus K,
\qquad
(\dim S_h,\dim L,\dim K)=(7,1,4).
\]

The analytic quotient-curved control proves a clean structural point:
nontrivial ambient holonomy is compatible with exact semantic behavior when
the null fiber is invariant and the cross blocks vanish. Ambient dynamics do
not have to be erased; they have to remain in the kernel of the declared
observation and continuation interface.

The learned arm reveals the complementary obstruction. A pointwise observer
can look correct while failing to define an invariant bundle. The missing
condition is a globally coherent connection: continuation must transport the
horizontal/vertical split without accumulating phase between them. In this
sense v0.6 replaces the old radial-instability problem with a sharper one:

\[
\text{bounded recurrence}
\;\not\Rightarrow\;
\text{invariant observable quotient}.
\]

Orthogonality fixes norm growth. It does not fix semantic phase drift.

There is also a structural limit on what the fixed ambient fiber can mean. If
all recurrent operators are isometries of one positive-definite metric and a
fixed observation kernel is invariant, its metric-orthogonal complement is
automatically invariant. The recurrence therefore block-diagonalizes. For an
exact finite-group representation such as D4, Maschke averaging gives an
invariant complement even without fixing a metric. Hence a nontrivial one-way
linear memory extension cannot be identified inside the present assumptions.
The proof and escape conditions are recorded in
`AMBIENT_SPLITTING_THEOREM.md`.

## Scientific conclusion

The strongest supported statement is:

> A compiled \(7\oplus1\oplus4\) ambient decomposition can exactly isolate a
> rank-seven centered-behavior quotient while allowing nontrivial,
> behaviorally inert curvature in a four-dimensional null fiber. Under the
> frozen v0.6 training recipe, however, the trained hard semantic block failed
> calibration and the unrestricted learned arm did not acquire an invariant
> rank-seven quotient; small local cross-block errors accumulated into large
> suffix-visible leakage.

The result does **not** establish a learned invariant kernel, useful ambient
memory, spontaneous Neuralese, architecture-independent emergence, awareness,
or consciousness.

## Consequence for the next block

The right response is not to lower v0.6 thresholds or consume seed 947. The
next design should separate three questions that v0.6 currently bundles:

1. **Semantic executor calibration.** Keep an analytically exact semantic
   block as the assay positive control. Treat a trained hard semantic block as
   a separate optimization question rather than as the sole prerequisite for
   testing the geometry.
2. **Exact learned splitting.** Test a learned projector or frame with
   generator parameterizations that enforce zero cross blocks by construction,
   for example a block-diagonal skew generator in the learned frame followed
   by an exponential or polar map. This asks whether the split can be learned
   without permitting phase leakage after it is selected.
3. **Product-level connection control.** Evaluate and, in a distinct arm,
   train on logarithmically spaced suffix lengths. One-step Frobenius means
   should be supplemented by worst-case product leakage and relation defects,
   because the present failure lives in composition rather than in a single
   generator.
4. **Separate memory algebra.** Retain D4 as the exact semantic quotient, but
   test useful ambient memory with typed `WRITE`, `HOLD`, and `QUERY` arrows,
   a contractive or nonlinear fiber update, or a phase-dependent kernel. Two
   histories should collide to the same quotient state while retaining
   different payloads that remain invisible until the registered query.

A successful successor must retain the exact-sequence and coordinate-covariant
interpretation while distinguishing a learned invariant fiber from a compiled
one. Until then, the honest v0.6 outcome is a useful calibration failure: the
ambient geometry is viable, the assay can see it, and the remaining obstacle
is global semantic transport.
