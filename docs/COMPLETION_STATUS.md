# Completion, Lean coverage and confidence

Recorded 2026-10-27 · **Komorebi P.**

[Filter by discipline, completion and proof evidence](https://KomorebiP.github.io/Operation-KOMOREBI/works.html) · [Browse the collection](BROWSE.md) · [Start here](START_HERE.md) · [Repository home](../README.md)

**Completion, Lean coverage and confidence describe different things.** A finished book may contain open research. A checked Lean proof may belong to an unfinished project. Choose a completion stage below, open a work's evidence record, then follow its paper, proofs, Lean, and code link.

This guide summarizes the existing release and status records at [source revision `080487d6401a`](https://github.com/KomorebiP/Operation-KOMOREBI/commit/080487d6401a7e9d90c415fd9ffbbf8d825e3842). It covers **90 primary components** and **71 supporting collections**. The labels report those records, rather than a new proof review or Lean run. Each recorded pass keeps its original date and scope.

[Finalization queue](FINALIZATION_QUEUE.md) · [Detailed evidence catalogue](STATUS_CATALOG.md) · [Component/file index](COMPONENT_INDEX.md) · [Machine-readable status](../manifests/project-status.json)

## Reader selection and soundness

Lean is optional. A clear written proof, exact finite certificate, or appropriately scoped experiment can support its own claim. File counts, formatting, and compilation alone do not establish soundness. The [records guide](RECORDS.md) brings together dated reviews, claim coverage, the files each record covers, and software checks. Read each report's scope and unresolved findings before relying on its conclusions.

Entries deferred from the main reading lists remain in the [incubator](INCUBATOR.md), with their source and status records intact. The component counts below describe the complete selected inventory, including those deferred entries.

## Completion stages

| Stage | Primary entries | Meaning |
|---|---|---|
| Scoped release | 10 | The release record marks the stated mathematical or executable requirements as complete. The scope below defines what is covered. |
| Reading edition complete | 41 | The stated manuscript or reader set is released. Formal coverage, review depth and wider research can remain incomplete. |
| Active development | 19 | A candidate, working manuscript or bounded research milestone with identified unfinished work. |
| Experiment / prototype | 12 | A research instrument, implementation or experiment whose tested scope does not establish a general scientific endpoint. |
| Reader available, source qualification pending | 1 | The PDF edition and reading scope have been identified. Matching editable sources, full page review, and reproducible build qualification remain pending. |
| Needs assessment | 6 | Available material lacks a sufficient assessed source/status record for a stronger label. |
| Earlier checkpoint | 1 | An earlier edition kept with its own evidence. Later acceptance records do not change that evidence. |

These categories describe the state of a work. They are not percentages or a ranking of mathematical importance. “Scoped release” means the stated release requirements are recorded as complete. Broader claims and implementations may remain unfinished. “Reading edition complete” means the stated manuscript or reader set has been released. It does not imply journal acceptance or a completed research program.

“Reader available” means the PDF edition and its reading scope have been identified. Matching editable sources, a full page review, and a reproducible build still need checking. This label does not establish mathematical confidence or a completed reading edition.

## Lean coverage

| Label | Meaning |
|---|---|
| Declared contract recorded | The cited release explicitly reports completion of its registered formal contract, under its exact hypotheses. |
| Selected results recorded | Compiler/replay evidence is reported for a subset or bounded block. No whole-work coverage is implied. |
| Inherited / related evidence | The edition relies on earlier or related formal evidence. That evidence is not a fresh full-edition replay. |
| Source available, no current pass | Lean text is present, but the assessed edition has no accepted current compiler pass. |
| No Lean claim | The assessed scope claims writing, calculations or experiments rather than Lean verification. |
| Not assessed | No formal-coverage assessment is made. |

“Declared contract” covers only the registered claims in the linked map. Modules, declarations, named theorems, proof bodies and finite test cases count different things, so their totals cannot be combined into a project completion percentage. A source map, file hash, Lean guide PDF or inventory does not establish that Lean accepted a proof. Evidence from an earlier edition keeps its own scope and does not certify a changed or expanded edition.

## Confidence basis

| Label | What supports confidence |
|---|---|
| Recorded formal evidence | Strong evidence for the exact checked subset, conditional on correct formal statements, source correspondence, dependencies and recorded execution. |
| Historical formal evidence | Earlier/related formal records support their own scope. Current-edition replay or expanded coverage may be missing. |
| Recorded written review | The cited edition records a scoped written review and/or proof audit with its stated depth. Finite checks support only their tested claims. |
| Written / finite evidence | Written arguments, author review or bounded computations. These records do not establish independent review or formal assurance. |
| Experimental evidence | Confidence is limited to the stated experiment, fixture, prototype or engineering tests. Generalization and scientific endpoints remain separate. |
| Unassessed | There is not enough assessed evidence for a confidence classification. |

Confidence labels identify the **strongest recorded evidence for the stated subset**. They do not assign a probability that the whole project is correct. A record can contain checked results alongside open or refuted claims. A written review covers only its stated scope and does not imply external peer review. Lean proofs still need correct hypotheses and a faithful match to the written statements. Experiments support claims about the populations, inputs and conditions actually tested.

All executable software remains **beta / work in progress**, including implementations attached to completed mathematical releases. See [LICENSE.md](../LICENSE.md) for the current reuse terms. Older undecided notices remain part of the historical record.

## Scoped release (10)

| Project and exact scope | Lean | Confidence basis |
|---|---|---|
| [Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates](STATUS_CATALOG.md#paper-i) | Declared contract recorded | Recorded formal evidence |
| [Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets](STATUS_CATALOG.md#paper-ii) | Declared contract recorded | Recorded formal evidence |
| [Paper X: Universal Residual Seeds and Conditional Occupied-System Completion](STATUS_CATALOG.md#paper-x) | Declared contract recorded | Recorded formal evidence |
| [Proof Path Theory](STATUS_CATALOG.md#proof-path-theory) | Selected results recorded | Recorded formal evidence |
| [Large Signal Model](STATUS_CATALOG.md#monographs-large-signal-model) | Declared contract recorded | Recorded formal evidence |
| [Certified Inference](STATUS_CATALOG.md#certified-inference) | Declared contract recorded | Recorded formal evidence |
| [Constructive Repair](STATUS_CATALOG.md#constructive-repair) | Selected results recorded | Recorded formal evidence |
| [Komorebi Space](STATUS_CATALOG.md#komorebi-space) | Declared contract recorded | Recorded formal evidence |
| [Realization Boundaries](STATUS_CATALOG.md#realization-boundaries) | Declared contract recorded | Recorded formal evidence |
| [Machine Native Reasoning](STATUS_CATALOG.md#monographs-machine-native-reasoning) | Declared contract recorded | Recorded formal evidence |

## Reading edition complete (41)

| Project and exact scope | Lean | Confidence basis |
|---|---|---|
| [Paper III: Typed Transfer, Nonlinear Packets, and Obstruction Theory](STATUS_CATALOG.md#paper-iii) | Selected results recorded | Recorded formal evidence |
| [Paper IV: Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data](STATUS_CATALOG.md#paper-iv) | Selected results recorded | Recorded formal evidence |
| [Paper V: Polyphase Signal Calculus](STATUS_CATALOG.md#paper-v) | Inherited / related evidence | Historical formal evidence |
| [Paper VI: Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations](STATUS_CATALOG.md#paper-vi) | Inherited / related evidence | Historical formal evidence |
| [Paper VII: Quantum Seed Calculus](STATUS_CATALOG.md#paper-vii) | Inherited / related evidence | Historical formal evidence |
| [Paper VIII: Packet Operator Algorithms, Exact Compilation, and GPU Realization](STATUS_CATALOG.md#paper-viii) | Inherited / related evidence | Historical formal evidence |
| [Paper IX: Arithmetic Packets, Dyadic Towers, and Local Polynomial Deformation](STATUS_CATALOG.md#paper-ix) | Selected results recorded | Recorded formal evidence |
| [Paper XI: Packets, Arithmetic Realization, and Conditional Comparison](STATUS_CATALOG.md#paper-xi) | Selected results recorded | Recorded formal evidence |
| [Paper XII: Patching Support, Hecke Packets, and Conditional Automorphic Completion](STATUS_CATALOG.md#paper-xii) | Inherited / related evidence | Historical formal evidence |
| [Realization Calculus](STATUS_CATALOG.md#realization-calculus-book) | Inherited / related evidence | Historical formal evidence |
| [Komorebi Methodology](STATUS_CATALOG.md#komorebi-methodology) | No Lean claim | Recorded written review |
| [Special Functions](STATUS_CATALOG.md#monographs-special-functions) | Selected results recorded | Recorded formal evidence |
| [Machine Societies](STATUS_CATALOG.md#monographs-machine-societies) | No Lean claim | Recorded written review |
| [Sufficient Resolution](STATUS_CATALOG.md#sufficient-resolution) | Inherited / related evidence | Historical formal evidence |
| [Quantum and Circuits](STATUS_CATALOG.md#monographs-quantum-and-circuits) | Selected results recorded | Recorded formal evidence |
| [Physics](STATUS_CATALOG.md#monographs-physics) | Selected results recorded | Recorded formal evidence |
| [COS Method](STATUS_CATALOG.md#monographs-cos-method) | Selected results recorded | Recorded formal evidence |
| [Self-Improving Intelligence](STATUS_CATALOG.md#monographs-self-improving-intelligence) | No Lean claim | Recorded written review |
| [Self-Improving Intelligence: visual guide](STATUS_CATALOG.md#monographs-self-improving-intelligence-visual-guide) | No Lean claim | Recorded written review |
| [Grounded Abstraction](STATUS_CATALOG.md#monographs-grounded-abstraction) | No Lean claim | Recorded written review |
| [Machine Understanding](STATUS_CATALOG.md#research-machine-understanding) | No Lean claim | Recorded written review |
| [OSL and Neuralese](STATUS_CATALOG.md#research-osl-neuralese) | No Lean claim | Experimental evidence |
| [OSL and Neuralese: reading edition](STATUS_CATALOG.md#research-osl-neuralese-reading-edition) | No Lean claim | Experimental evidence |
| [Stratified Recursive Improvement Closure](STATUS_CATALOG.md#research-stratified-recursive-improvement) | No Lean claim | Experimental evidence |
| [AVOC](STATUS_CATALOG.md#research-avoc) | Inherited / related evidence | Historical formal evidence |
| [Hypergraph Lumpability and Bayesian Refinement](STATUS_CATALOG.md#research-hypergraph-bayesian-refinement) | No Lean claim | Recorded written review |
| [Certified Bayesian Inference](STATUS_CATALOG.md#research-certified-bayesian-inference) | Inherited / related evidence | Historical formal evidence |
| [Stratified Relational Workspace Theory](STATUS_CATALOG.md#research-stratified-relational-workspace) | No Lean claim | Recorded written review |
| [ABC: source and evidence reader](STATUS_CATALOG.md#abc-reader) | Selected results recorded | Recorded formal evidence |
| [Beal: source and evidence](STATUS_CATALOG.md#beal-reader) | Selected results recorded | Recorded formal evidence |
| [Catalan Constant: source and evidence](STATUS_CATALOG.md#catalan-constant-reader) | No Lean claim | Recorded written review |
| [Collatz and Riemann: source and evidence](STATUS_CATALOG.md#collatz-and-riemann-readers) | No Lean claim | Recorded written review |
| [Hilbert 12: cubic divisor development](STATUS_CATALOG.md#hilbert12-cubic-divisor) | Selected results recorded | Recorded formal evidence |
| [Hodge: source and evidence](STATUS_CATALOG.md#hodge-reader) | Source available, no current pass | Recorded written review |
| [Inverse Galois: source and evidence](STATUS_CATALOG.md#inverse-galois-reader) | No Lean claim | Recorded written review |
| [Lehmer: source and evidence](STATUS_CATALOG.md#lehmer-reader) | No Lean claim | Recorded written review |
| [The Possibility for a Machine Native Mathematics](STATUS_CATALOG.md#machine-native-mathematics-essay) | No Lean claim | Unassessed |
| [Prime-Contact Coherence Calculus](STATUS_CATALOG.md#prime-contact-coherence) | No Lean claim | Recorded written review |
| [Signal Reconstruction](STATUS_CATALOG.md#signal-reconstruction) | Inherited / related evidence | Historical formal evidence |
| [Stratified Universality](STATUS_CATALOG.md#stratified-universality) | Source available, no current pass | Recorded written review |
| [Strong Artin: source and evidence](STATUS_CATALOG.md#strong-artin-reader) | Inherited / related evidence | Historical formal evidence |

## Active development (19)

| Project and exact scope | Lean | Confidence basis |
|---|---|---|
| [Information Realization](STATUS_CATALOG.md#information-realization) | Selected results recorded | Recorded formal evidence |
| [KZFC and Residual Reflection](STATUS_CATALOG.md#kzfc-multiverse) | Selected results recorded | Recorded formal evidence |
| [Logical Resolution](STATUS_CATALOG.md#logical-resolution) | Selected results recorded | Recorded formal evidence |
| [p-adic Canonical Realization](STATUS_CATALOG.md#padic-canonical-realization) | Selected results recorded | Recorded formal evidence |
| [Representation Calculus](STATUS_CATALOG.md#representation-calculus) | Selected results recorded | Recorded formal evidence |
| [COS Method: formal continuation](STATUS_CATALOG.md#monographs-cos-method-formal-continuation) | Selected results recorded | Recorded formal evidence |
| [Machine Native Reasoning: wider continuation](STATUS_CATALOG.md#research-machine-native-reasoning-wider) | Inherited / related evidence | Historical formal evidence |
| [ABC: global RR8 branch](STATUS_CATALOG.md#abc-global-rr8) | No Lean claim | Recorded written review |
| [AddMul Arithmetic Reconstruction](STATUS_CATALOG.md#addmul-arithmetic-reconstruction) | Selected results recorded | Recorded formal evidence |
| [Euler Signal Bridge](STATUS_CATALOG.md#euler-signal-bridge) | No Lean claim | Written / finite evidence |
| [Hilbert 12: ambient dual slice](STATUS_CATALOG.md#hilbert12-ambient-dual-slice) | No Lean claim | Written / finite evidence |
| [Hilbert 12: analytic Fourier branch](STATUS_CATALOG.md#hilbert12-analytic-fourier) | No Lean claim | Written / finite evidence |
| [Hilbert 12: closure attempt](STATUS_CATALOG.md#hilbert12-closure-attempt) | No Lean claim | Written / finite evidence |
| [Hilbert 12: contracting ambient torsion](STATUS_CATALOG.md#hilbert12-contracting-ambient-torsion) | No Lean claim | Written / finite evidence |
| [IUT Valuation Hulls](STATUS_CATALOG.md#iut-valuation-hulls) | Selected results recorded | Recorded formal evidence |
| [Model-Theory Normalization](STATUS_CATALOG.md#model-theory-normalization) | Selected results recorded | Recorded formal evidence |
| [Resolution Semantics](STATUS_CATALOG.md#resolution-semantics) | Source available, no current pass | Written / finite evidence |
| [Seeded Two-Axis Calculus](STATUS_CATALOG.md#seeded-two-axis) | No Lean claim | Written / finite evidence |
| [Streaming Polyphase Factor Decomposition / SKAT](STATUS_CATALOG.md#streaming-skat) | No Lean claim | Written / finite evidence |

## Experiment / prototype (12)

| Project and exact scope | Lean | Confidence basis |
|---|---|---|
| [Agent Dynamics](STATUS_CATALOG.md#experiments-agent-dynamics) | No Lean claim | Experimental evidence |
| [Arithmetic J-Space Training Lab](STATUS_CATALOG.md#experiments-arithmetic-jspace) | No Lean claim | Experimental evidence |
| [J-Space Causal Lab](STATUS_CATALOG.md#experiments-jspace-causal-lab) | No Lean claim | Experimental evidence |
| [J-Space Collections](STATUS_CATALOG.md#experiments-jspace-collections) | No Lean claim | Experimental evidence |
| [Workspace Incubator](STATUS_CATALOG.md#experiments-workspace-incubator) | No Lean claim | Experimental evidence |
| [RRCT multispace convergence protocol](STATUS_CATALOG.md#research-rrct-multispace-protocol) | No Lean claim | Experimental evidence |
| [RRCT](STATUS_CATALOG.md#packages-rrct) | No Lean claim | Experimental evidence |
| [SRIC: external semantic admission](STATUS_CATALOG.md#research-sric-external-admission) | No Lean claim | Experimental evidence |
| [SRIC: endogenous semantic witness](STATUS_CATALOG.md#research-sric-block23-witness) | No Lean claim | Experimental evidence |
| [PRISM-1R](STATUS_CATALOG.md#research-prism-1r) | No Lean claim | Experimental evidence |
| [PRISM-1](STATUS_CATALOG.md#research-prism-1) | No Lean claim | Experimental evidence |
| [Universal Generative Deformation Calculus](STATUS_CATALOG.md#universal-generative-deformation) | No Lean claim | Experimental evidence |

## Reader available, source qualification pending (1)

| Project and exact scope | Lean | Confidence basis |
|---|---|---|
| [Gaussian Elimination: collected guide](STATUS_CATALOG.md#gaussian-elimination-guide) | Not assessed | Unassessed |

## Needs assessment (6)

| Project and exact scope | Lean | Confidence basis |
|---|---|---|
| [Large Signal Model software](STATUS_CATALOG.md#large-signal-model) | Not assessed | Unassessed |
| [Machine Theory Compendium](STATUS_CATALOG.md#machine-theory-compendium) | Not assessed | Unassessed |
| [Physics: curvature states](STATUS_CATALOG.md#physics-curvature-states) | Not assessed | Unassessed |
| [Physics: energy and backreaction](STATUS_CATALOG.md#physics-energy-backreaction) | Not assessed | Unassessed |
| [Physics: origin locking](STATUS_CATALOG.md#physics-origin-locking) | Not assessed | Unassessed |
| [Realization Calculus: twin edition](STATUS_CATALOG.md#realization-calculus-twin-edition) | Not assessed | Unassessed |

## Earlier checkpoint (1)

| Project and exact scope | Lean | Confidence basis |
|---|---|---|
| [Machine Theory: formal development](STATUS_CATALOG.md#research-machine-theory-formal) | Selected results recorded | Recorded formal evidence |

## Supporting and earlier material

The **71 supporting collections** are listed separately in the [evidence catalogue](STATUS_CATALOG.md#supporting-and-historical-collections). Their import receipts identify the available files. This guide does not reassess their mathematics or transfer a newer edition's coverage and completion label to them.

| Additional material | Status in this assessment |
|---|---|
| [Research Preview 1](../formal/research-preview-1) | Earlier import, not reassessed here. Consult its own formal records and their stated scope. |
| [Quadratic-Form Engine / K-COS (earlier edition)](../papers/quadratic-form-kcos) | Earlier import. Use the current COS monograph and separate formal continuation for the current assessment. |
| [AM-SPD](../packages/komorebi-am-spd) | Earlier import. The software remains beta / work in progress. No new scientific assessment is reported here. |
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | Independent Python library in beta / work in progress. Qualification is tracked in that repository. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | Independent C library in beta / work in progress. Qualification is tracked in that repository. |

## Maintaining the distinctions

Maintainers can edit the assessments and cited evidence in `manifests/project-status.json`, then run `python tools/update_completion_status.py`. Use `--check` to validate IDs, evidence bindings and generated pages without writing them. The component index uses the same labels. A changed source, expanded statement or new accepted run requires a reviewed status update. Uploading files alone does not change their completion or confidence status.

To strengthen a formal status, supply the exact claim map, pinned source and environment, accepted compiler and axiom records, appropriate controls, and any required review of how the formal and written statements correspond. To finalize a reading edition, identify its editable source and matching PDF, complete the relevant build and page checks, and preserve its mathematical scope. Wider research and experimental goals remain separate queue items.

[Browse the collection](BROWSE.md) · [Finalization queue](FINALIZATION_QUEUE.md) · [Records guide](RECORDS.md)
