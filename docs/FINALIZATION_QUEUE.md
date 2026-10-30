# Cleanup and finalization queue

[Browse the collection](BROWSE.md) · [Completion guide](COMPLETION_STATUS.md) · [Evidence catalogue](STATUS_CATALOG.md)

Recorded 2026-10-27. This queue tracks documentation, research, formalization and experimental work. An item marked done has met its stated completion requirements. Progress on an open item leaves its remaining requirements in place. Use the item links below to read those requirements, then follow the work links to its paper, proofs, Lean, and code.

**Current maintenance focus:** Repository navigation, edition records, and reproducibility instructions are the current maintenance priority. Further proof reviews are deferred. Their existing findings and completion requirements remain open. All software remains beta / work in progress.

## Queue at a glance

| Item | Status | Work to complete |
|---|---|---|
| [F01](#f01) | done | Separate current and historical status |
| [F02](#f02) | done | Make completion, Lean and confidence independently visible |
| [F03](#f03) | open | Reconcile the expanded Machine-Native Reasoning book |
| [F04](#f04) | open | Resolve Paper IV visual-guide source correspondence |
| [F05](#f05) | open | Replay editions that currently rely on inherited formal evidence |
| [F06](#f06) | open | Resolve uncompiled or unverified Lean source |
| [F07](#f07) | open | Assess the two reader-only entries |
| [F08](#f08) | done | Close the Constructive Repair release-candidate checklist |
| [F09](#f09) | done | Consolidate Streaming SKAT version navigation |
| [F10](#f10) | open | Complete bounded proof and submission reviews |
| [F11](#f11) | open | Extend selected formal cores only against explicit claim maps |
| [F12](#f12) | open | Run the missing empirical and hardware campaigns |
| [F13](#f13) | ongoing | Preserve the open-endpoint register |
| [F14](#f14) | ongoing | Review substantive support before reader promotion |
| [F15](#f15) | done | Repair and qualify SRIC Block 24 admission gates |
| [F16](#f16) | open | Assess the newly imported source collections |

## Completed cleanup and bounded qualification

<a id="f01"></a>

<a id="f01--separate-current-and-historical-status"></a>

### F01: Separate current and historical status

**Status: done**

The current core is 27/27. The older 23/27 checkpoint and working wider manuscript retain their own labels.

**Done when:** Status pages link each edition and its own evidence. Source packages remain byte-preserved.

Related works and source records: [Machine Theory: formal development](works/research-machine-theory-formal.md) · [Machine Native Reasoning](works/monographs-machine-native-reasoning.md) · [Machine Native Reasoning: wider continuation](works/research-machine-native-reasoning-wider.md).

<a id="f02"></a>

<a id="f02--make-completion-lean-and-confidence-independently-visible"></a>

### F02: Make completion, Lean and confidence independently visible

**Status: done**

All primary components receive distinct stage, Lean, confidence, scope, evidence and next-step fields.

**Done when:** Every selected component is represented once. Supporting sources remain separately classified.

Coverage: all primary entries in the [status guide](COMPLETION_STATUS.md).

<a id="f08"></a>

<a id="f08--close-the-constructive-repair-release-candidate-checklist"></a>

### F08: Close the Constructive Repair release-candidate checklist

**Status: done**

The mathematical contract and kernel/Python distinction must survive package finalization.

**Done when:** Repeat the documented package checks on supported platforms, publish an exact source-to-wheel mapping, and reference the current collection license.

**Progress:** 30 October 2026: published the [qualified beta](https://github.com/KomorebiP/Operation-KOMOREBI/releases/tag/constructive-repair-1.0.0rc3-qualified-e58a66e5e5fc). Linux / CPython 3.13.5 passed all 100 release tests; Windows Server 2025 / CPython 3.13.5 passed 97 with the three named POSIX-only skips. Both platforms passed the two symlink controls, 134 engine tests, and 72 installed cases with 369 probe checks. The final gate verified both source archives and byte-identical wheels bound to the seven original runtime files. Current license/README metadata is recorded in a separate build overlay. All seven public assets were downloaded and hash-checked, and both extracted archives passed their verifier. Original source and earlier failure records are preserved. No fresh Lean replay is claimed.

Related works and source records: [Constructive Repair](works/constructive-repair.md).

<a id="f09"></a>

<a id="f09--consolidate-streaming-skat-version-navigation"></a>

### F09: Consolidate Streaming SKAT version navigation

**Status: done**

A maintained edition guide now separates the v0.8 manuscript and 0.8.0 marker from the v0.9 simulation continuation and historical v0.5/v0.6 entry points.

**Done when:** Create a current edition map and entry point, reconcile the current manuscript/tests, and preserve earlier records with their original dates.

**Progress:** Linked the manuscript/source pair, theorem index, seven-suite historical 31-test census, copy-LD correction, and open numerical/empirical boundaries. The original source package is unchanged. No fresh test, simulation, or Lean replay is claimed.

Related works and source records: [Streaming Polyphase Factor Decomposition / SKAT](works/streaming-skat.md).

<a id="f15"></a>

<a id="f15--repair-and-qualify-sric-block-24-admission-gates"></a>

### F15: Repair and qualify SRIC Block 24 admission gates

**Status: done**

The three reproduced admission/provenance defects are repaired in the separate 0.3.3 beta source runtime.

**Done when:** Publish a separately identified corrected edition with rejection controls, preserved synthetic positive fixture, and source-bound evidence.

**Progress:** 15 test methods passed locally, including all 48 NaN positions, provenance failures, finite mismatch, and a custom-path CLI round trip. Original 0.3.2 evidence remains intact. Real-model execution and wider qualification remain open under F12.

Related works and source records: [SRIC: external semantic admission](works/research-sric-external-admission.md).

## Next finishing work

<a id="f03"></a>

<a id="f03--reconcile-the-expanded-machine-native-reasoning-book"></a>

### F03: Reconcile the expanded Machine-Native Reasoning book

**Status: open**

The selected core is complete. The exact expanded 1,155-page edition needs its own source and reader reconciliation.

**Done when:** Identify the exact source/PDF hashes, reconcile core correspondence, rebuild the book, and complete its own publication review.

Related works and source records: [Machine Native Reasoning: wider continuation](works/research-machine-native-reasoning-wider.md) · [Machine Native Reasoning](works/monographs-machine-native-reasoning.md).

<a id="f04"></a>

<a id="f04--resolve-paper-iv-visual-guide-source-correspondence"></a>

### F04: Resolve Paper IV visual-guide source correspondence

**Status: open**

The latest visual PDF lacks a recovered exact matching editable source.

**Done when:** An authenticated matching source or explicitly new reconstructed edition has a documented PDF/text comparison and page review.

Related works and source records: [Paper IV: Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data](works/paper-iv.md).

<a id="f05"></a>

<a id="f05--replay-editions-that-currently-rely-on-inherited-formal-evidence"></a>

### F05: Replay editions that currently rely on inherited formal evidence

**Status: open**

These editions do not have a fresh whole-edition Lean replay in the assessed publication record.

**Done when:** Pinned sources/dependencies, accepted builds, exact declaration/axiom checks and appropriate controls are saved under new receipts. Coverage is not enlarged by replay.

Related works and source records: [Sufficient Resolution](works/sufficient-resolution.md) · [AVOC](works/research-avoc.md) · [Strong Artin: source and evidence](works/strong-artin-reader.md) · [Paper V: Polyphase Signal Calculus](works/paper-v.md) · [Paper VI: Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations](works/paper-vi.md) · [Paper VII: Quantum Seed Calculus](works/paper-vii.md) · [Paper VIII: Packet Operator Algorithms, Exact Compilation, and GPU Realization](works/paper-viii.md) · [Paper XII: Patching Support, Hecke Packets, and Conditional Automorphic Completion](works/paper-xii.md).

<a id="f06"></a>

<a id="f06--resolve-uncompiled-or-unverified-lean-source"></a>

### F06: Resolve uncompiled or unverified Lean source

**Status: open**

Source text or static inventories are not compiler acceptance.

**Done when:** Compile the exact intended source with pinned dependencies, record diagnostics and axioms, and map accepted statements to the manuscript. Retain missing mathematical inputs.

Related works and source records: [Resolution Semantics](works/resolution-semantics.md) · [Hodge: source and evidence](works/hodge-reader.md) · [Stratified Universality](works/stratified-universality.md).

<a id="f07"></a>

<a id="f07--assess-the-two-reader-only-entries"></a>

### F07: Assess the two reader-only entries

**Status: open**

Availability alone does not establish an editorial or mathematical completion level.

**Done when:** Identify the edition, editable sources, claim scope and actual review/build records, then replace the unassessed labels.

**Progress:** The machine-native mathematics essay has a separately identified 25-page reading edition with editable sources, inspected typesetting, local mathematical clarifications, and source-reconciled accounts of the current papers and selected companion studies. Its scientific confidence remains unassessed. The original editable source, the Gaussian Elimination entry, and independent scientific review requirements remain open.

Related works and source records: [Gaussian Elimination: collected guide](works/gaussian-elimination-guide.md) · [The Possibility for a Machine Native Mathematics](works/machine-native-mathematics-essay.md).

## Proof and submission review

<a id="f10"></a>

<a id="f10--complete-bounded-proof-and-submission-reviews"></a>

### F10: Complete bounded proof and submission reviews

**Status: open**

Existing review scopes do not cover all proofs or establish external submission readiness.

**Done when:** Record statement-specific reviews, resolve findings, and keep literature priority and empirical review distinct from proof correctness.

**Progress:** Machine Societies has 38 distinct reviewed pairs of 62: 36 recorded passes and two qualifications. 24 remain unreviewed. Batch 4 adds five passes and identifies the missing event-emitting compilation premise in thm:undecidable. That restriction and its certificate consequence, plus the earlier finite-index condition for prop:memory, need a revised source edition. Neither qualified statement is counted as a pass. Other listed review obligations remain open.

Related works and source records: [Machine Societies](works/monographs-machine-societies.md) · [Hypergraph Lumpability and Bayesian Refinement](works/research-hypergraph-bayesian-refinement.md) · [Stratified Relational Workspace Theory](works/research-stratified-relational-workspace.md) · [Seeded Two-Axis Calculus](works/seeded-two-axis.md).

<a id="f14"></a>

<a id="f14--review-substantive-support-before-reader-promotion"></a>

### F14: Review substantive support before reader promotion

**Status: ongoing**

Lean is optional. Precise statements, sufficient arguments or appropriately bounded evidence, and honest completion claims are required.

**Done when:** Review the exact claims and evidence for each proposed promotion, resolve identified defects, and record the reviewer and source revision. A finite pass or listing decision cannot certify a whole program.

**Progress:** Seven small entries screened. Three focused mathematical claims reviewed. Two incomplete implementation entries moved to the incubator. Remaining manuscripts and analytic dependencies are not certified by this pass.

Related works and source records: [Euler Signal Bridge](works/euler-signal-bridge.md) · [Hilbert 12: ambient dual slice](works/hilbert12-ambient-dual-slice.md) · [Resolution Semantics](works/resolution-semantics.md) · [Hilbert 12: analytic Fourier branch](works/hilbert12-analytic-fourier.md) · [Hilbert 12: contracting ambient torsion](works/hilbert12-contracting-ambient-torsion.md) · [PRISM-1R](works/research-prism-1r.md) · [RRCT multispace convergence protocol](works/research-rrct-multispace-protocol.md).

<a id="f16"></a>

<a id="f16--assess-the-newly-imported-source-collections"></a>

### F16: Assess the newly imported source collections

**Status: open**

Thirteen additional collections were imported before the availability and assessment indexes were synchronized. Importing source files does not establish soundness or completion.

**Done when:** Map the seven primary works and six supporting collections to their exact editions and claims, inspect applicable written proofs or experimental records, and update readiness and confidence with explicit evidence.

**Progress:** All 166 component receipts now reconcile with the committed paths, blob identities, modes, and aggregate record digests. The 13 new records remain scientifically unassessed.

Related works and source records: [ARC-AGI-2 experiment](works/arc-agi2.md) · [Offline handoff](STATUS_CATALOG.md#arc-agi2-offline-handoff) · [Original solver](STATUS_CATALOG.md#arc-agi2-original-solver) · [Public evaluation](STATUS_CATALOG.md#arc-agi2-public-evaluation) · [Training evidence](STATUS_CATALOG.md#arc-agi2-training-evidence) · [Recovery v14](STATUS_CATALOG.md#certified-inference-recovery-v14-supporting-sources) · [Large Signal Model software](works/large-signal-model.md) · [Supporting sources](STATUS_CATALOG.md#large-signal-model-ancestry-supporting-sources) · [Machine Theory Compendium](works/machine-theory-compendium.md) · [Physics: curvature states](works/physics-curvature-states.md) · [Physics: energy and backreaction](works/physics-energy-backreaction.md) · [Physics: origin locking](works/physics-origin-locking.md) · [Realization Calculus: twin edition](works/realization-calculus-twin-edition.md).

## Formal, mathematical and empirical development

<a id="f11"></a>

<a id="f11--extend-selected-formal-cores-only-against-explicit-claim-maps"></a>

### F11: Extend selected formal cores only against explicit claim maps

**Status: open**

Publication completion and checked subresults leave wider formal or implementation obligations.

**Done when:** Choose one precise next theorem/refinement contract, establish its dependencies, and admit it only with corresponding source and verification evidence.

Related works and source records: [Paper III: Typed Transfer, Nonlinear Packets, and Obstruction Theory](works/paper-iii.md) · [Special Functions](works/monographs-special-functions.md) · [Quantum and Circuits](works/monographs-quantum-and-circuits.md) · [Signal Reconstruction](works/signal-reconstruction.md) · [COS Method: formal continuation](works/monographs-cos-method-formal-continuation.md) · [p-adic Canonical Realization](works/padic-canonical-realization.md) · [Model-Theory Normalization](works/model-theory-normalization.md).

<a id="f12"></a>

<a id="f12--run-the-missing-empirical-and-hardware-campaigns"></a>

### F12: Run the missing empirical and hardware campaigns

**Status: open**

Fixtures, candidate diagnostics and interface skeletons do not establish real-model or hardware endpoints.

**Done when:** Use frozen inputs and gates, retain failures, execute held-out/replicated tests or hardware compilation/measurement, and report the actual tested scope.

Related works and source records: [SRIC: external semantic admission](works/research-sric-external-admission.md) · [SRIC: endogenous semantic witness](works/research-sric-block23-witness.md) · [RRCT multispace convergence protocol](works/research-rrct-multispace-protocol.md) · [RRCT](works/packages-rrct.md) · [Arithmetic J-Space Training Lab](works/experiments-arithmetic-jspace.md) · [Workspace Incubator](works/experiments-workspace-incubator.md) · [PRISM-1](works/research-prism-1.md) · [PRISM-1R](works/research-prism-1r.md).

<a id="f13"></a>

<a id="f13--preserve-the-open-endpoint-register"></a>

### F13: Preserve the open-endpoint register

**Status: ongoing**

These broad mathematical or physical endpoints are research obligations, not editorial cleanup.

**Done when:** Promote only an exact newly proved obligation with its hypotheses and review/formal evidence. Finite checks and a released book cannot close an open endpoint.

Related works and source records: [Paper X: Universal Residual Seeds and Conditional Occupied-System Completion](works/paper-x.md) · [Paper XI: Packets, Arithmetic Realization, and Conditional Comparison](works/paper-xi.md) · [Paper XII: Patching Support, Hecke Packets, and Conditional Automorphic Completion](works/paper-xii.md) · [ABC: global RR8 branch](works/abc-global-rr8.md) · [ABC: source and evidence reader](works/abc-reader.md) · [Beal: source and evidence](works/beal-reader.md) · [Catalan Constant: source and evidence](works/catalan-constant-reader.md) · [Collatz and Riemann: source and evidence](works/collatz-and-riemann-readers.md) · [Hilbert 12: closure attempt](works/hilbert12-closure-attempt.md) · [Hilbert 12: cubic divisor development](works/hilbert12-cubic-divisor.md) · [Hodge: source and evidence](works/hodge-reader.md) · [Inverse Galois: source and evidence](works/inverse-galois-reader.md) · [Lehmer: source and evidence](works/lehmer-reader.md) · [Strong Artin: source and evidence](works/strong-artin-reader.md) · [Physics](works/monographs-physics.md).

## Release discipline

Keep accepted source packages and dated failures intact. New claims or corrected mathematics belong in a new edition with its own evidence. A control counts as a successful rejection check only when it fails for the intended mathematical reason. Missing imports, timeouts and unavailable runtimes do not establish proof rejection. Conditional results keep their assumptions after editorial work is complete.

The [current reuse terms](../LICENSE.md) explain how retained historical undecided notices are handled. Navigation can clarify those terms while preserving historical source files and third-party terms.

[Browse the collection](BROWSE.md) · [Completion guide](COMPLETION_STATUS.md) · [Records guide](RECORDS.md)
