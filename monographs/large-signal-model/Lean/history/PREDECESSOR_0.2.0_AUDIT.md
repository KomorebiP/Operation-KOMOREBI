# Large Signal Model — Lean 0.2.0 audit

**Komorebi P. · 10 October 2026 · Frozen Foundations 1.0.0**

## Result and scope

This block completes the reviewed formal mappings of P3 and P8. The cumulative coverage is **10 complete, no partial and 77 unformalized propositions**. The completed set is P1, P2, P3, P4, P5, P6, P7, P8, P10 and P22. Foundations 1.0.0 and production PR-LASM 2.3.0 are unchanged.

Five new proof modules are added to the ten inherited modules. There are **135 explicitly named theorem declarations**, comprising **101 foundation/supporting theorems and 34 example-module theorems**. The new block contributes 64 theorems, 20 of them in its example module. There are **190 explicitly named declarations** including definitions, structures, an inductive tree type and a named Fintype instance. Automatically generated constructors, recursors, equation lemmas and compiler auxiliaries are not separately counted. Their environment is included in module replay.

These are not independent-novelty or difficulty-weighted progress counts. Coverage refers to correspondence with the numbered manuscript statements under their recorded hypotheses, not to all surrounding prose or to production-code correctness. The kernel checks the Lean statements. It does not mechanically certify the English-to-Lean translation.

## P3: a genuine tree and complete-cut proof

`PacketTree` is an inductive finite rooted tree with finite nonempty children at internal nodes. A Boolean selection is complete precisely when its count on every full root-to-leaf path is one. The root-only and recursive-child alternatives are derived from that condition, rather than used as a substitute definition that assumes conservation.

The generic conservation result applies to additive labels using only local parent/child sums. It is converted to a conventional Fintype sum over selected node addresses. Applying it to linear maps gives the identity operator and signal reconstruction. Applying it to squared norms gives the energy identity after a separately proved local Pythagorean argument.

Sibling range orthogonality is a local hypothesis. It follows from the manuscript's self-adjoint orthogonal projector products through `range_orthogonal_of_projector_products`. Global cut reconstruction and energy equality are conclusions. The development works for real or complex inner-product spaces and permits mixed depths and arbitrary finite branching.

The formalization does not include a best-basis optimization algorithm, a proof of probability positivity for signed packets or a claim that deleted branches remain reconstructive.

## P8: finite stabilization and constructed realization

The enrichment sequence consists of actual submodules, sums and operator images. Strict enlargement increases dimension; a contradiction with the ambient dimension proves stabilization by the dimension-deficit bound. Equality at one step persists. The explicitly indexed completion is proved invariant and least among all invariant extensions containing the initial subspace.

Applied to dual pullbacks, this becomes the row-observable construction of P8. Lean constructs the evaluation state and its reduced transition, and proves algebraic surjectivity in finite dimension. It also constructs finite-basis coordinate maps with linearly independent rows, exact initial readout and exact action transitions. A separate result proves minimality against any competing closed linear summary with an exact linear readout.

The state and basis constructions are noncomputable Lean mathematics, not executable row reduction. The operators are supplied and known. No finite-data identification of unknown operators, unknown rank or an accessible measuring device is inferred. The surrounding single-operator Cayley–Hamilton discussion is not marked as an additional checked result.

The rational three-coordinate example proves that the actual completion is exactly the row space annihilating the third coordinate. It contains the first and second coordinate rows and excludes the third. It is a proper subspace, not a nominal reduction that always keeps the whole signal.

## Fresh source build, axiom audit and module replay

`verification/release_run/report.json` records the successful source-candidate run:

| Check | Observed result |
|---|---:|
| Proof modules compiled | 15 |
| Root import compiled | 1 |
| Explicit declarations in axiom inventory | 190 |
| Modules replayed with the upstream kernel routine | 15 |
| Deliberately invalid files correctly rejected | 11 |
| Metadata and tooling records | 26 |

The verifier deletes the project build directory first. It checks Lean's exact commit and all nine dependency Git revisions, then uses one worker with warnings treated as errors. It records commands, source hashes, return codes, durations and output. The source snapshot is rechecked at completion. No saved PASS or project compiled object is reused.

All 190 observed axiom sets are subsets of `propext`, `Classical.choice` and `Quot.sound`. Thirty-two explicitly named declarations have no axiom dependencies. The others use various subsets of the whitelist. Basis/representative choice is explicit; no claim of an axiom-free development is made.

The pinned upstream `LeanChecker.replayFromImports` function is invoked separately on each module. This is additional kernel replay within Lean, not a second proof assistant. Imported Mathlib modules are trusted as pinned compiled dependencies and are not all rebuilt or freshly replayed. Standard upstream replay infrastructure is not introduced as a new mathematical assumption.

The source scanner finds no custom mathematical axiom, admitted placeholder, native-decision shortcut or unsafe definition in active proof sources. It is supplementary validation, not the mathematical basis of kernel checking.

## Rejection controls

The six inherited controls remain unchanged. Five new controls fail on concrete false claims about an uncovered root-to-leaf path, overlapping selections, energy preservation without orthogonality, a first-coordinate-only transition and an invented third-coordinate value. They are excluded from the root import.

Each rejection has a nonzero Lean exit, an actual proof diagnostic, no timeout and no missing-module or failed-import explanation. The dedicated placeholder control is rejected with warnings as errors. Expected rejection is not counted as a positive theorem.

The 26 Python checks are separately labeled metadata/tooling records. They reconcile the declaration inventory and source locations, complete coverage map and unchanged manuscript hashes, all ten inherited proof files, 91 unchanged predecessor declaration records, root/import order, new targets, theorem categories and failure handling of the axiom-record parser.

## Source preservation and runtime provenance

The original Lean 0.1.0 archive is preserved in `history/` with its exact SHA-256 in `SOURCE_LINEAGE.json`. All ten inherited proof source files are byte-identical. Both frozen Foundations 1.0.0 source files are also byte-identical. Older verification records are explicitly labeled as predecessor evidence rather than presented as current runs.

The runtime was restored from all seven user-provided `Lean_Offline_*.zip` parts. Each chunk and the complete compressed stream were hashed; ZIP reads check CRC. The combined SHA-256 is `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`. Extraction completed with exit zero. The record is `verification/runtime_restore_block2.json`.

The actual compiler is Lean 4.34.0-rc2 at commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Execution used Linux x86-64, Python 3.13.5, one Lean worker and a 4 GiB memory ceiling. Runtime binaries and caches are not redistributed in this source bundle.

## Development failures and repairs

Twenty-six recorded development invocations include both successful and failing compilations or API probes. Failing attempts are preserved with the attempted source and full diagnostics under `verification/development_block2/`. They are not counted as accepted proofs.

The initial tree implementation needed explicit reduction of dependent node types and a bridge to the actual `Fintype.sum_sum_type`/`sum_sigma` interfaces. A class-valued recursive enumeration needed the appropriate reducibility annotation. The energy proof initially swapped the inner-product indices in an off-diagonal term. Correcting the index order retained the full real/complex theorem.

The completion development initially guessed a nonexistent `Mathlib.Tactic.Omega` import and encountered inequality orientation, dimension inference and basis-instance elaboration issues. The final version uses the installed pinned interfaces. Several independence proofs hit Lean's default elaboration heartbeat limit. They were replaced by a direct finite-support linear-combination argument; the accepted files do not raise the heartbeat budget or assume row independence. Unused section variables and simplifier arguments were removed rather than disabling warning checks.

Example compilation exposed dependent finite-index reductions and an unsuitable automatic product extensionality step. Explicit linear-map extensionality and algebraic expansion fixed those proofs. No desired reconstruction, energy, finite stabilization or minimality conclusion was moved into an unproved hypothesis to get a compilation pass.

The final strict source-candidate build, axiom audit, fifteen module replays and eleven intended rejections all completed successfully. There was no compiler download attempt, fresh statistical experiment or runtime extraction failure in this block. The older archive retains its own separately dated failure history.

## Delivery and remaining formal work

The ZIP contains source, metadata, scripts, guides, the preserved predecessor archive and relevant execution evidence. Project compiled objects, runtime binaries, Python caches and transient process files are excluded. `MANIFEST.json` lists every other payload file. Hash verification and complete inventory comparison must precede commands that regenerate reports or caches.

The delivered archive is extracted into a separate directory with no copied project build artifacts and the full verifier is rerun there. Its actual hash, inventory, compilation, axiom, replay and rejection results are in the separately delivered extraction-verification JSON. This audit does not contain a self-referential archive hash.

P9/P12 finite inference compatibility is the next natural sector. The probability-domain, continuous-observation, approximation-learning and sequential-confidence propositions remain unformalized. No independent referee review, different proof assistant, Windows execution, online Lake rebuild, remote CI, publication or license change is claimed.
