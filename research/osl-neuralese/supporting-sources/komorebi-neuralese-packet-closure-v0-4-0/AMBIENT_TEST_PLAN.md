# Ambient semantic-packet test plan

## Purpose

This block asks whether the learned projective recurrence carries semantics on robust regions of ambient projective space, or whether its apparent closure is explained by broad decoder cells, finite-horizon agreement, anchor-only trajectories, or a table-driven shortcut.

The central object is a context-indexed semantic map

\[
\pi_c:\mathcal R_c\rightarrow X
\]

that should satisfy the semiconjugacy law

\[
\pi_c(\widehat M_{c,g}[h])=g\cdot\pi_c([h]).
\]

Here \(\widehat M\) denotes the induced positive-projective action. The claim is not that all ambient activations must be identical or path-flat. It is that different representatives of one proposed semantic fiber must have the same declared causal continuations and must evolve into the same successor fiber.

## Evidence firewall

The following v0.2 observations motivated this block:

- positive radial scale is an exact gauge of the bias-free recurrence
- the centered decoder is instantaneously rank seven
- finite future observability is full rank eight
- no fixed additive future-null subspace was found
- terminal-only projective training greatly delayed depth failure
- null cycles preserved labels while moving hidden rays
- the exact semantic chart achieved bounded exact execution

These are retrospective diagnostics. In addition, small read-only calibration runs on the same frozen seeds informed the implemented packet, gauge, and switching thresholds. The resulting v0.3 audit is therefore developmental and posthoc with respect to model selection. It cannot provide a confirmatory emergence estimate.

Within the implemented run, all trajectory contexts, prefixes, exhaustive packet suffixes, switched words, and null-loop repetitions are deterministically fixed before model execution. The packet audit applies the same declared exhaustive suffix set at each reachable prefix; it is not a construction-versus-heldout packet-generalization test. Editing a bank, threshold, or diagnostic constant changes the source or contract digest and requires a new run.

Version 0.3 implements the diagnostic foundation and the reachable-state portions of Phases 0, 3, 4, and 5 below. Optimized same-packet pair construction, relation-grouped construction/heldout suffix splitting, broad off-manifold certification, shuffled/reset controls, and context-naturality training remain explicitly scheduled extensions rather than silently omitted pass conditions.

## Definitions

For a word \(u\), let

\[
y_u(h)=\arg\max_j (D M_u h)_j.
\]

The finite behavioral signature is

\[
\sigma_K([h])=(y_u(h))_{|u|\le K}.
\]

A discovery packet is the set of states whose discovery-bank signature matches the required signature for abstract state \(i\). This is a candidate empirical cell, not an assumed intrinsic meaning.

With linear homogeneous dynamics, each finite packet is an intersection of homogeneous halfspaces. It is normally a full-dimensional polyhedral projective cell. Therefore its ordinary tangent space at an interior point is the whole ambient projective tangent space. The experiment will not equate “tangential” with “harmless.” It will measure distance to pulled-back future decision boundaries.

For target class \(F_u(i)\), competitor \(j\), and

\[
a_{uij}=M_u^{\mathsf T}(w_{F_u(i)}-w_j),
\]

the ambient metric distance to that boundary is

\[
r_{uij}(h)=
\frac{a_{uij}^{\mathsf T}h}
{\sqrt{a_{uij}^{\mathsf T}G^{-1}a_{uij}}}.
\]

The reported continuation radius is the minimum across all audited \(u,j\), together with its projective-tangent analogue. Current-output margin alone is not a robustness measure.

## Phase 0: validate the assay — implemented

Before interpreting a learned checkpoint, the v0.3 runner must pass four calibration families.

1. **Checkpoint and episode integrity.** Checkpoint hashes/configurations, intermediate states, targets, and visible operator slots must agree with the inherited records and exact transition tables.
2. **Gauge controls.** The harness must recover exact global and statewise positive scale, reject negative scale as an oriented-projective gauge, and reconstruct injected off-ray leakage.
3. **Exact semantic chart.** The supplied permutation action in the canonical chart must produce exact continuation packets and unit switched gain. This is an engineered positive control.
4. **Nonnormal switch.** Individually contractive matrices with an unstable switched product must be flagged by the product-level diagnostic.

Delayed-observability, suffix-split, and leakage-return constructions have unit-test coverage, but v0.3 does not promote them to recorded pilot assay gates. Shuffled-action and reset-executor baselines remain future work.

Failure of a calibration invalidates the assay rather than the model.

## Phase 1: construct nontrivial candidate packets — future

Candidate pairs are constructed in a normalized \(G\)-chart using only discovery inequalities through length eight. Constrained optimization must enforce:

- the same discovery signature
- discovery margin at least \(10^{-3}\)
- projective separation at least \(0.05\) radians
- no use of heldout correctness

The report includes feasibility by abstract state and context, pair separation, discovery inradius, active constraints, and failure cases. If only infinitesimal neighborhoods around anchors are feasible, the robust-packet hypothesis fails its nontriviality gate.

## Phase 2: audit heldout continuation and congruence — future

For every certified pair \(([h],[h'])\), evaluate a disjoint suffix bank.

Two separate questions are scored:

1. Do both representatives produce the same correct continuation signature?
2. For every generator \(g\), do \(M_g h\) and \(M_g h'\) enter the same correct successor packet under the heldout bank?

The second question is essential. Finite equivalence normally loses one horizon after each update:

\[
h\sim_{K+1}h'\Longrightarrow M_g h\sim_K M_g h'.
\]

Only representative-independent successor behavior supports a quotient operator. Fit-bank inclusion receives no success gate because it follows largely from construction.

## Phase 3: search for delayed semantic return — partially implemented

The implemented runner evaluates the actual reachable state at prefixes 0, 64, 128, and 256 against every binary continuation through horizon 8. This measures whether the state remains inside its required finite continuation packet and records the minimum normalized boundary margin. The nested cells

\[
\mathcal K_i^{(0)}\supseteq\mathcal K_i^{(1)}\supseteq\cdots
\]

remain the broader target. A later construction/heldout experiment should report:

- signature agreement separately at every depth
- packet inradius and tenth-percentile margin versus horizon
- first divergence depth for every pair
- whether the apparent packet shrinks toward one ray or loses robust interior

The current result reports every prefix separately so no average hides late failure. Agreement through finite \(K\) is never described as proof of infinite-horizon equivalence.

## Phase 4: audit switched and nonnormal dynamics — implemented at fixed scope

Radial normalization does not control angular amplification. For reachable \([h]\), compute the projective differential

\[
D\widehat M_g([h])v
=
\frac{\Pi_{\widehat{M_gh}}M_gv}{\|M_gh\|_G}.
\]

At prefix 64, v0.3 exhaustively evaluates all 256 binary words of length 8 in 32 D4 contexts per seed. It reports product tangent gain, mixed-versus-constant switching enhancement, minimum pre-normalization image norm, semantic margin, and behavioral accuracy. Random longer switching and beam-search adversaries remain future extensions.

Individual matrix spectral radii, average trajectory norms, and finiteness after normalization are diagnostics only. They cannot satisfy the switched-stability gate.

## Phase 5: distinguish harmless from harmful holonomy — implemented at fixed scope

At prefix 64, v0.3 inserts the D4 relations \(f^2\), \(r^4\), and \(frfr\), repeated 1, 2, 4, 8, 16, and 32 times. It then evaluates the same exhaustive continuation packet through horizon 8. At every repeat count it records:

- endpoint label accuracy
- full heldout continuation signature
- projective displacement from the no-loop state
- robust continuation radius
- pre/post margin ratio
- first semantic boundary crossing

Conjugated relators, additional commutators, and disjoint heldout suffixes remain future extensions. Nonzero holonomy is called harmless only while the audited orbit remains in the same finite packet with positive margin. A loop that is correct at its endpoint but changes a later suffix is harmful semantic leakage.

## Phase 6: perturb away from anchor trajectories — future

The model is tested on four matched intervention classes:

1. certified within-discovery-packet perturbations
2. equal-angle perturbations constructed to cross a discovery boundary
3. random tangent perturbations
4. adversarial tangent perturbations minimizing heldout margin

Angles are fixed at \(0.01\), \(0.05\), and \(0.10\) radians. The report separates reachable perturbations, locally reachable perturbations, and arbitrary ambient perturbations. Success only on the eight state anchors does not support an ambient packet claim.

## Phase 7: context and transport naturality — future

Transport is fitted using a restricted subset of states, operators, and contexts. It is frozen before evaluating heldout states, conjugacies, operator families, and continuations.

Three different properties are reported:

\[
\pi_c(M_{c,g}h)=g\cdot\pi_c(h),
\]

\[
T_{c,c'}M_{c,g}\approx M_{c',\phi(g)}T_{c,c'},
\]

and

\[
\pi_{c'}T_{c,c'}\approx\phi\pi_c.
\]

Hidden-state reconstruction alone is not the target. Behavioral continuation, causal edits, and commuting residuals must all be evaluated. A positive-projective transport is homogeneous and linear. If an affine offset is used, it is reported as a different model and ablated.

## Phase 8: baseline discrimination — partially implemented

The exact semantic chart and synthetic nonnormal/gauge controls are implemented. The remaining rows specify the next baseline block.

| Baseline | What it prevents us from claiming |
|---|---|
| Exact semantic chart | Its perfect performance cannot be called learned emergence |
| Table lookup executor | Task success alone does not imply abstract operator discovery |
| Nearest-anchor reset | Packet semiconjugacy alone does not distinguish continuous algebra from classify-and-reset execution |
| Decoder temperature or wide-cell control | Large current margins do not establish future stability |
| Shuffled-table control | Shape, norm, or lexical correspondence is insufficient |
| Synthetic time bomb | Finite-horizon agreement is not an infinite semantic fiber |
| Synthetic nonnormal switch | Stable individual spectra do not imply stable switching |
| Norm and gradient controls | Projective training gains may reflect optimization conditioning rather than semantic geometry |

The lookup and reset systems are expected to solve much of the finite task. Their success is not a failed negative control. It establishes the level of evidence that cannot distinguish an operator algebra from a finite-state executor.

## Interpretation and falsification

The v0.3 package adjudicates only the exact A01–A08 assay gates, M01–M05 learned-mechanism references, and C01–C02 capability references recorded in `AMBIENT_PREREGISTRATION.json`. The broader robust ambient-packet claim would require the future phases above. Interpret failures locally:

- failure of heldout agreement rejects continuation stability at that horizon
- failure of representative congruence rejects a well-defined quotient action
- collapse of inradius rejects a nontrivial robust packet
- failure after null loops rejects harmless-holonomy language
- switch failure rejects robust recurrent stability
- off-manifold failure restricts the claim to anchor trajectories
- transport failure rejects coordinate-natural shared semantics
- equivalence to reset or lookup retains a finite-state execution claim but blocks an emergent ambient-algebra claim

Even a complete developmental pass would support only task-relative, finite-audit semantic fibers. It would not prove an infinite-horizon quotient, observer-independent meaning, spontaneous Neuralese, or subjective awareness.
