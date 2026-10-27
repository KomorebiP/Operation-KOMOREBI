# Large Signal Model — Lean 0.1.0 audit

**Komorebi P. · 10 October 2026 · Foundations theory 1.0.0**

## Result and mathematical boundary

This is the first compiled formalization block for the frozen LSM foundations. Ten proof modules contain **71 named theorem declarations**, of which **57** are foundation/supporting theorems and **14** are exact examples or counterexamples. There are **91 named declarations** including the definitions, structure and abbreviation. Declaration counts are not novelty counts or difficulty-weighted progress.

The reviewed source mapping covers the numbered statements of **P1, P2, P4, P5, P6, P7, P10 and P22** under the explicit hypotheses in `COVERAGE.md`. **P3 is partial**, covering complete-family reconstruction and one finite regrouping layer. Its general rooted-tree, complete-antichain and orthogonal energy theorem is not included. **78 propositions remain unformalized.** None appears as an unfinished theorem imported by the root module.

This is not a formalization of the whole production implementation. PR-LASM 2.3.0 is unchanged. The two frozen Foundations 1.0.0 source files included under `source/` are unchanged, with exact hashes in `SOURCE_LINEAGE.json`. No previous Komorebi project's proof counts or Python examples are included in the new Lean declaration count. Imported Mathlib results provide their usual library foundation.

## Claims checked as constructions, not assumed outputs

The quotient proof constructs the reduced map from fiber constancy and proves uniqueness on the actual image. The atlas proof uses a realizable-coefficient subtype, rather than assuming every ambient redundant coefficient is valid. Its converse supplies a reference chart explicitly, so the chart family is nonempty. Total operations are covered; surrounding prose about partial-map domains is not claimed as an additional theorem here.

The transfer proofs use actual linear maps, finite sums and intermediate projector idempotence. The polynomial theorem retains every ordered multilinear packet interaction. The normed results use actual continuous linear maps and their operator norms. Nontriviality of the observation space is explicit before division by the synthesis norm.

The memory result includes recurrence elimination, reindexing, specialization to actual projected dynamics, a continuous-linear-map bridge, a geometric tail bound and the unresolved initial-state term. The full-minus-truncated bound evaluates both expressions on **the same history**. It does not prove stability of recursively generated approximate trajectories. The refinement obstruction includes the set-level factorization, linear kernel criterion and worst-case half-distance error bound.

These statement correspondences have been reviewed against the frozen text. The kernel checks the Lean declarations themselves; it does not mechanically establish that an English paragraph was translated correctly. P2's reference-chart condition and all coverage restrictions remain visible in the mapping.

## Actual local verification

`verification/release_run/report.json` records a successful fresh local run:

| Check | Result |
|---|---:|
| Proof modules compiled | 10 |
| Aggregator compiled | 1 |
| Named declarations in exact axiom inventory | 91 |
| New proof modules replayed through the kernel | 10 |
| Deliberately invalid controls rejected | 6 |
| Metadata and tooling regression records | 18 |

Compilation uses one worker and `-DwarningAsError=true`. The build output directory is deleted before verification. No cached PASS is reused. Exact commands, source hashes, exit codes, stdout, stderr and durations appear in the report. The source snapshot is checked again at the end. The metadata checks are separate from mathematical proof counts.

All 91 reported axiom dependency sets are subsets of **`propext`, `Classical.choice`, `Quot.sound`**. Several elementary declarations have no axiom dependencies. The representative construction uses classical choice openly. There is no claim that the whole development is axiom-free.

Active proof sources contain no custom `axiom`, admitted placeholder, `native_decide`, unsafe definition or proof-escape command. The scanner is an additional defense, not the basis of proof correctness. The six intentionally failing controls are kept outside the import graph: false arithmetic, a placeholder, missing coefficient consistency, dropped closure, dropped nonlinear interactions and invented refinement. Their actual diagnostics show the intended mathematical or placeholder rejection, not a missing import or timeout.

## What kernel replay means here

The wrapper in `scripts/ReplayModule.lean` imports the pinned upstream **LeanChecker** and calls its own `replayFromImports` function separately for each new module. That function reconstructs the module's incoming environment and asks the kernel to replay its new constants. It is the same implementation used by the standard `leanchecker` command, with directory-wide module discovery bypassed.

This is an additional replay within Lean, **not an independent proof assistant**. It does not rebuild or freshly replay every imported Mathlib theorem. Standard upstream I/O/replay infrastructure has unsafe implementation internals; those are not imported as mathematical assumptions or written into the proof library. Its source SHA-256 is recorded in the verification report.

## Toolchain and runtime provenance

The checked runtime is **Lean 4.34.0-rc2**, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The verifier checks all nine dependency Git revisions in `lake-manifest.json`. These revision checks and the restored archive identify the imported environment; they are not independent proofs of every upstream binary or declaration.

The runtime was restored from the user's seven `Lean_Offline_*.zip` parts. The combined archive SHA-256 is `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`, matching its prior recorded value. The restoration record is included. This source release does not redistribute the multi-gigabyte compiler and dependency cache.

Execution used Linux and Python 3.13.5, with a 4 GiB memory ceiling. The WSL PowerShell wrapper is supplied but was not executed on Windows. The conventional Lake configuration is pinned, but a fresh online `lake update` was not run. The direct offline verifier is the executed and documented route.

## Failed attempts and repairs

The initial online compiler download failed because the container could not resolve GitHub. The offline kit replaced that route. The first archive extraction exceeded a tool execution window. Recovering only selected parts initially left a required Mathlib server artifact unavailable; the remaining archive contents were then restored and targeted imports worked. No partial extraction was treated as a successful proof environment.

Development builds exposed incorrect import guesses, finite-sum rewriting and indexing issues, missing normed-operator imports, deprecation warnings, an elaboration ambiguity and a tactic-focus lint. These were corrected using the actual pinned library interfaces. Captured source snapshots and diagnostics appear in `verification/development/`. No desired conclusion was replaced by an unproved mathematical assumption to obtain a successful build.

The generic `leanchecker` entry point scans the dependency tree when discovering modules. A combined run did not complete within the tool window. A second combined invocation was also interrupted. Their reports remain explicitly incomplete. The final accepted run instead calls the pinned upstream per-module replay function and records successful exits for all ten modules. It does not turn the interrupted runs into passes or weaken kernel checking.

An additional metadata regression initially counted 88 declarations instead of 91 because its independent counting regex omitted three same-line `@[simp]` attributes. The inventory and Lean axiom output were already correct. The regex was repaired without changing a Lean proof or declaration. All 18 metadata/tooling checks then passed, including deliberate rejection of missing, extra, duplicate, truncated and unapproved axiom records.

## Delivery and reproducibility

The ZIP is a source handoff with one top-level project directory. It contains the proof sources, exact source lineage, complete coverage ledger, guides, verifier, development diagnostics and successful local report. Compiled objects, runtime binaries and transient process records are excluded. A SHA-256 manifest covers its declared payload; the external ZIP checksum anchors that manifest.

The delivered archive is extracted separately and the same full verifier is rerun without copied compiled objects. Its complete hash/inventory check and actual compilation, axiom audit, replay and rejection outcomes are recorded in the **separately delivered extraction report**. Keeping that report outside the archive avoids a self-referential archive hash. Read its actual result before asserting that a particular extraction passed.

No new statistical experiment, probability-domain theorem, independent referee review, remote CI, GitHub publication or license change is claimed. The next mathematical targets are P3's full tree/energy result and P8's finite-dimensional minimal completion.
