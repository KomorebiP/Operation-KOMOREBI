# Neuralese Causal Completion Surface

Author: Komorebi P.  
Version: 0.3.0  
Date: 2026-09-03  
Status: adaptive developmental follow-up; specification frozen before any v0.3.0 learned-checkpoint run

## Purpose and claim boundary

This block measures the two-index finite causal object

\[
Q^{I}_{L,H}=R_{\leq L}/\!\sim^{I}_{H},
\]

where (L) bounds the histories admitted into the reachable domain, (H) bounds future continuations, and (I) declares the observation interface. The primary interfaces are:

- **hard:** the ordered tree of decoded class decisions;
- **probability:** the ordered tree of softmax probability vectors;
- **centered logit:** the ordered tree of logits after removing their scalar-shift gauge.

The learned checkpoints are frozen. There is no fitting, retraining, metric learning, centroid retraction, or threshold tuning in this block.

This is an adaptive developmental follow-up to v0.2.1, whose outcomes were known before this specification was written. In particular, v0.2.1 found an exact finite hard-decision quotient on its ordinary-history window, nonzero soft microstate variation, and continuation-visible drift under repeated identity words. Consequently, v0.3.0 is not confirmatory and its D4 episodes are not held-out table-pair support. It is a sharper exhaustive audit of a declared finite rectangle plus a separate adversarial witness family.

## Frozen inputs

Only the two projective-terminal checkpoints are scientific inputs:

| Checkpoint | SHA-256 |
|---|---|
| `projective_terminal_seed0.pt` | `b2d16d640dddc4f2f2ed69a4211f0d9948c71c3655901484238fa8ae11c1f702` |
| `projective_terminal_seed1.pt` | `a52dd3def596553c2880dfd00516bd1bb7492d1cbfab1634b570f27c1737d2d7` |

Weights are read with the inherited restricted NumPy loader. The recurrence is evaluated in float64 and normalized after every generator application. A pre-normalization norm at or below (10^{-12}), or any nonfinite state, norm, logit, probability, or reported statistic, is an execution failure; it must not be silently repaired by clipping.

For checkpoint seed (s\in\{0,1\}), eight deterministic D4 coordinate-resampled episodes are generated from

```text
np.random.default_rng(930000 + 1000 * s)
sample_batch(..., batch_size=8, length=0, family="d4")
```

The sampled start field is ignored and all eight starts are enumerated. Canonical generator words use `0 = R` and `1 = F`; every canonical word is converted through that episode's `canonical_to_slot` map before learned execution. Exact semantics are advanced with the episode's integer maps. Signature identifiers and all quotient comparisons are episode-local; episodes are never pooled into a shared coordinate chart.

These episode seeds are fresh relative to the v0.2.1 audit seeds. Fresh coordinate draws do not make the table pairs held out: the checkpoint's reconstructed D4 training support covers the finite table-pair family used here.

## Exact completion rectangle

The registered rectangle is

\[
0\leq L\leq 8,\qquad 0\leq H\leq 8.
\]

For every checkpoint, episode, and start, all binary canonical histories of every length (0,\ldots,8) are enumerated. From each history node, all binary canonical suffixes of every length (0,\ldots,8) are enumerated. A single trajectory tree to total depth (16) may share computation, but the scientific domain is the exact Cartesian history/suffix window, not a sample.

For one episode the registered counts at cell ((L,H)) are:

\[
n_{\mathrm{hist}}^{\le L}=8(2^{L+1}-1),\qquad
n_{\mathrm{hist}}^{=L}=8\,2^L,
\]

\[
n_{\mathrm{suf}}^{\le H}=2^{H+1}-1,\qquad
n_{\mathrm{suf}}^{=H}=2^H.
\]

The primary cumulative cell contains

\[
n_{\mathrm{decision}}^{\le L,\le H}
=n_{\mathrm{hist}}^{\le L}n_{\mathrm{suf}}^{\le H}
\]

declared decisions, even when trajectory nodes are computationally shared.

### Collision-free hard signatures

Let (widehat y(x)) be the decoded class at a normalized learned state (x). The cumulative future signature is defined recursively in canonical generator order:

\[
\sigma_0(x)=\widehat y(x),
\]

\[
\sigma_h(x)=
\bigl(\widehat y(x),\sigma_{h-1}(F_Rx),\sigma_{h-1}(F_Fx)\bigr).
\]

Implementation may intern these exact integer tuples for efficiency. Hash digests alone are forbidden: tuple equality must resolve hash collisions. Intern tables are scoped by episode and horizon, and integer IDs from different episodes or horizons have no shared meaning. For testing, (sigma_h) must equal explicit breadth-first enumeration of every suffix decision through depth (h).

For history domain (X_L), either cumulative (R_{\le L}) or the exact shell (R_{=L}), define:

\[
\operatorname{split}_{L,H}
=\max_q\left|\{\sigma_H(x):x\in X_L,\ s(x)=q\}\right|,
\]

\[
\operatorname{merge}_{L,H}
=\max_t\left|\{s(x):x\in X_L,\ \sigma_H(x)=t\}\right|,
\]

where (s(x)) is the exact current D4 semantic state. A split is history-dependent hard microstate at the declared future horizon. A merge is failure to distinguish semantic states under that interface.

Every cell reports:

- exact history, suffix, and decision counts;
- semantic continuation accuracy and an all-decisions-correct flag;
- number of signature classes;
- maximum within-semantic split multiplicity;
- maximum semantic labels per signature;
- fraction of the eight semantic labels that are individually correct, unsplit, and unmerged;
- minimum, first percentile, and median target margin over the declared decisions;
- all zero-norm and nonfinite counters.

The primary surface uses histories (leq L) and futures (leq H). An exact-history shell (=L) is reported with the same cumulative future signature. Accuracy, margin, and soft-interface summaries are also reported for exact future shell (=H), including the exact-history/exact-future shell. Shell results localize first failures but do not replace the cumulative completion gate and are not required to be monotone.

### Hard completion criterion

An episode-level cumulative cell passes only if all of the following hold:

1. every declared prediction equals its exact D4 continuation target;
2. every target margin is finite and strictly positive;
3. exactly eight hard signature classes occur;
4. maximum split multiplicity is exactly one;
5. maximum merge multiplicity is exactly one;
6. all eight semantic labels have completion fraction one;
7. no invalid numerical event occurs.

There is no (0.99) relaxation. A seed-level cell passes only if all eight episodes pass. The registered rectangle gate passes only if all 81 cumulative cells pass for both seeds. The cumulative pass mask must be a down-set: if a cell fails, no cell with both greater-or-equal (L) and greater-or-equal (H) may pass. A down-set violation is an implementation/audit failure, not a scientific recovery.

## Soft interfaces remain separate

Hard signature identity is not probability or logit identity. For a history state (x), define ordered cumulative signatures

\[
P_H(x)=\operatorname{concat}_{|w|\le H}
\operatorname{softmax}(z(F_wx)),
\]

\[
Z_H(x)=\operatorname{concat}_{|w|\le H}
Cz(F_wx),
\qquad
C=I-\frac18\mathbf 1\mathbf 1^{\mathsf T}.
\]

Suffix coordinates use a fixed breadth-first canonical-word order. For every episode, cell, semantic label, interface, and declared history window, report scalar-normalized within-label RMS deviation from the within-label mean, the maximum label-wise RMS, and the maximum within-label coordinate range. Probability and centered-logit statistics are never mixed with hard quotient class counts.

The diagnostic **exact soft-collapse** gate uses numerical-identity tolerances, not a tuned notion of approximate semantics:

- maximum probability coordinate range within a semantic label (leq10^{-10});
- maximum centered-logit coordinate range within a semantic label (leq10^{-10}\max(1,\max|Cz|)).

Both conditions must hold in every episode and every cumulative cell. Failure means only that the exact eight-class soft quotient is absent on this rectangle. RMS dispersion remains descriptive; no post-hoc soft-stability threshold may be substituted.

## Diagonal action compatibility

A generator does not automatically define a same-cell endomorphism of (Q_{L,H}). It increases admitted past depth by one and consumes one unit of future discrimination. The directly justified finite map is diagonal:

\[
F_a:Q_{L,H+1}\longrightarrow Q_{L+1,H}.
\]

For every (0\leq L,H\leq7), episode, source signature class, and generator (a), v0.3.0 checks that all members of the source class produce one target signature class and that the induced semantic label agrees with the episode's exact D4 action. This diagonal gate passes only with exact agreement everywhere.

Even a pass does not establish a closed action on one stabilized quotient, an invariant metric, or indefinite recurrence. Same-space closure would additionally require compatible stabilization as both axes extend beyond the registered rectangle.

## Separate repeated-relator witness family

The completion rectangle stops at (L=8). A distinct adversarial family probes much longer, algebraically redundant histories without pretending to enumerate the corresponding ordinary-history domains.

### Base histories

For every checkpoint and each of its eight registered episodes, enumerate:

- all (2^6=64) canonical base histories of exact depth six;
- all eight semantic starts.

This gives 512 base cases per episode. From each reached state compare a no-insertion baseline, an identity insertion, and a length-matched nonidentity insertion. Every comparison exhausts suffix horizons (H=0,\ldots,8).

### Identity words and budgets

The four registered canonical relation paths are:

| Name | Canonical word |
|---|---|
| `r4` | `(R,R,R,R)` |
| `f2` | `(F,F)` |
| `frfr` | `(F,R,F,R)` |
| `rfrf` | `(R,F,R,F)` |

`frfr` and `rfrf` are algebraically redundant identity relations but distinct ordered learned paths; they are not treated as independent statistical evidence.

For relation (r), use repeat counts (k\in\{1,2,4,8,16,32\}) filtered by (k|r|\le64). Thus `f2` uses inserted-token budgets `2,4,8,16,32,64`, and each length-four relation uses `4,8,16,32,64`. The exact D4 action of every repeated relation must be identity before learned execution.

### Matched nonidentity control

For a repeated identity insertion (v=r^k), the matched control has identical length and identical first (|v|-1) canonical symbols, with only the final symbol toggled:

\[
\widetilde v=(v_1,\ldots,v_{|v|-1},1-v_{|v|}).
\]

Its exact D4 action must be nonidentity; otherwise execution stops. This controls path length and almost the entire ordered prefix. It is a deterministic mechanism sanity check, not an iid control group or a causal estimate.

### Relator endpoints

For every relation, budget, base case, episode, seed, and cumulative or exact suffix shell through (H=8), report:

- loop-versus-baseline hard signature survival and first revealing suffix horizon;
- loop and baseline semantic continuation accuracy;
- minimum target margin and loop-minus-baseline margin change;
- positive-ray endpoint distance and angle, with negative rays distinct;
- paired probability-signature RMS/max difference;
- paired centered-logit-signature RMS/max difference;
- the same correctness, margin, and numerical checks for the matched nonidentity path against its own exact semantic target;
- whether the control endpoint decision differs from baseline as exact semantics require.

The hard relator-closure gate requires survival `1.0`, semantic accuracy `1.0`, strictly positive margins, and no invalid numerics for every identity insertion and every suffix through (H=8). The soft/path-flatness gate additionally requires maximum unit-ray L2 distance (le10^{-8}), maximum paired probability difference (le10^{-10}), and maximum paired centered-logit difference (le10^{-10}\max(1,\max|Cz|)) everywhere. The matched-control sanity gate requires verified nonidentity ground truth, exact semantic continuation accuracy, positive margins, and endpoint disagreement with baseline in every case.

A single identity-loop hard disagreement is a counterexample to unconditional completion at its observed history depth and horizon. Passing this finite relation family is only survival of that family; it is not a certificate for all histories of the same length.

## Registered gates

| Gate | Exact pass rule | Interpretation of a pass |
|---|---|---|
| `E0_execution_integrity` | checkpoint digests, restricted loading, counts, slot conversion, tuple recursion, finite/nonzero execution, and structural tests all exact | the audit executed as declared |
| `H0_hard_rectangle` | every cumulative cell for both seeds and all episodes satisfies the hard completion criterion | finite hard completion on the exact (L,H\le8) rectangle |
| `H1_downset` | cumulative hard pass mask is a down-set | internal consistency of exact cumulative reporting |
| `S0_soft_exact_collapse` | both soft interfaces satisfy their numerical-identity bounds in every cumulative cell | exact eight-class soft collapse only on the registered rectangle |
| `D0_diagonal_action` | every declared (Q_{L,H+1}\to Q_{L+1,H}) map is well-defined and equals the D4 action | finite diagonal compatibility, not same-space stabilization |
| `W0_relator_hard_closure` | every identity insertion survives all suffixes through H8 with exact correctness and positive margin | no hard counterexample in this registered witness family |
| `W1_relator_soft_flatness` | every identity insertion satisfies ray, probability, and centered-logit identity tolerances | numerical path flatness only for the registered paths |
| `C0_nonidentity_control` | every matched control has nonidentity ground truth and exact correct behavior through H8 | long-path task sensitivity under the deterministic matched control |

There is no omnibus threshold that converts a mixed gate profile into success. Each gate is reported separately. The strongest permitted statement is the conjunction of the gates that actually pass, with their finite domains named.

## Required structural validation before learned endpoints

Synthetic or hand-constructed tests may run before the learned audit. They must include:

1. vectorized trajectory-tree parity with scalar recurrence;
2. recursive-signature equality with explicit suffix tuples through at least (H=3);
3. exact history and suffix count formulas;
4. handcrafted coherent, split, merge, and wrong-but-coherent cases;
5. generator-slot swap identity under `canonical_to_slot`;
6. episode isolation and rejection of cross-episode signature-ID comparison;
7. zero-norm and nonfinite fail-closed behavior;
8. cumulative down-set validation;
9. positive versus negative ray handling;
10. regression of the inherited v0.2.1 ordinary (L=6,H=3) hard result on the inherited audit episodes, kept separate from the fresh v0.3.0 surface.

The v0.3.0 runner and its digest must be frozen after structural validation and before learned scientific endpoints are inspected. If a scientific-code defect is found afterward, the first run is preserved, the change is documented, and a new explicitly adaptive version is created; results are not silently overwritten.

## Outputs and aggregation

Machine-readable outputs must retain seed and episode identifiers and include cumulative and shell tables. Human summaries may show worst-case, median, or mean values only when the underlying per-seed/per-episode records remain available. Gates use worst-case conjunction, not pooled means. There are two checkpoint seeds, so no population inference, p-value, or architecture-level confidence claim is registered.

The final package must include this specification, its machine-readable preregistration, frozen runner/test digests, checkpoint digests, raw per-cell records or losslessly reconstructible summaries, gate results, limitations, a manifest, and a clean-extraction verification command.

## Explicit exclusions

No result in this block alone establishes:

- a quotient beyond (L,H\le8);
- exhaustive ordinary-history behavior at relator depths (6+B>8);
- a same-space stabilized quotient or unbounded recurrence;
- equality of probability laws from hard-decision equality;
- contraction of an identified vertical semantic fiber;
- an invariant metric or joint-spectral certificate;
- a global semantic atlas or architecture-independent transport;
- spontaneous Neuralese in frontier language models;
- consciousness or awareness.

The scientific value of the block is narrower and concrete: it makes the finite ((L,H)) claim exact, keeps hard and soft interfaces distinct, checks the only directly justified diagonal action, and subjects the apparent completion to a declared family of long identity-path counterexamples.
