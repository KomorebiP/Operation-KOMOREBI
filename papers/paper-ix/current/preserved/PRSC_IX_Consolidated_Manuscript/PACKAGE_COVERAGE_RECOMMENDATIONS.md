# Paper IX package coverage recommendations

Prepared for the next cumulative Paper IX release. This is a read-only inventory of the existing cumulative stage and the known local project roots. No staging files were edited.

## Scope and result

Compared `/workspace/scratch/196a43c5b4f3/release_staging/PRSC_IX_Dyadic_Isometries` against `inputs`, `upload`, `work`, `review`, `native_work`, `edge_recovery`, `brainstorm_open`, `least_periods`, `strengthening`, `shared_correction`, `dyadic_isometry`, and all seven previous local output ZIPs. Files were compared using SHA-256 rather than names. The original baseline ZIP was also indexed by the hashes of its uncompressed entries.

There are **38 recommended additions totaling 407,977 bytes**, listed below. These include the omitted general Mahler-kernel experiment, the earliest strengthening checkpoint, historical inventories, recovered source windows, and standalone development audit drivers. All active proof source files from the audited prior release are already represented. Every relevant noncompiled file under `work/` is already covered by a hash in the cumulative stage or its preserved baseline ZIP.

The new polynomial lifting block is being developed concurrently and is outside this prior-state inventory. Add its final sources, controls, scripts, logs, manifest and audit after its verification completes.

## Exact additions

Source paths below are absolute. Destination paths are relative to the new cumulative package root. `package_coverage_copies.json` provides the same map with SHA-256 values for automated assembly.

| Source | Desired relative destination | Bytes |
| --- | --- | ---: |
| `/workspace/scratch/196a43c5b4f3/brainstorm_open/kernel/check_kernel_formulas.py` | `research/mahler_kernel/check_kernel_formulas.py` | 7,667 |
| `/workspace/scratch/196a43c5b4f3/brainstorm_open/kernel/kernel_check_results.json` | `research/mahler_kernel/kernel_check_results.json` | 2,752 |
| `/workspace/scratch/196a43c5b4f3/brainstorm_open/kernel/kernel_check_manifest.json` | `research/mahler_kernel/kernel_check_manifest.json` | 2,494 |
| `/workspace/scratch/196a43c5b4f3/brainstorm_open/MANIFEST.json` | `historical/release_metadata/OPEN_QUESTIONS_ROUTES_MANIFEST.json` | 848 |
| `/workspace/scratch/196a43c5b4f3/output/Nishibuchi_Strengthening_Notes/README.md` | `historical/initial_strengthening/README.md` | 5,489 |
| `/workspace/scratch/196a43c5b4f3/output/Nishibuchi_Strengthening_Notes/reproduce_early_rows.py` | `historical/initial_strengthening/reproduce_early_rows.py` | 765 |
| `/workspace/scratch/196a43c5b4f3/output/Nishibuchi_Strengthening_Notes/early_row_check.json` | `historical/initial_strengthening/early_row_check.json` | 803 |
| `/workspace/scratch/196a43c5b4f3/output/Nishibuchi_Strengthening_Notes/computation_manifest.json` | `historical/initial_strengthening/computation_manifest.json` | 2,180 |
| `/workspace/scratch/196a43c5b4f3/output/Nishibuchi_Strengthening_Notes/reproduction.log` | `historical/initial_strengthening/reproduction.log` | 73 |
| `/workspace/scratch/196a43c5b4f3/output/Nishibuchi_Strengthening_Notes/MANIFEST.json` | `historical/initial_strengthening/MANIFEST.json` | 466 |
| `/workspace/scratch/196a43c5b4f3/release_staging/PRSC_IX_Sharp_Dyadic_Continuation/MANIFEST.json` | `historical/release_metadata/SHARP_DYADIC_MANIFEST.json` | 36,390 |
| `/workspace/scratch/196a43c5b4f3/release_staging/PRSC_IX_Sharp_Dyadic_Continuation/strengthening/inventory.json` | `historical/release_metadata/SHARP_DYADIC_INVENTORY.json` | 18,216 |
| `/workspace/scratch/196a43c5b4f3/release_staging/PRSC_IX_Exact_Dyadic_Periods/strengthening/inventory.json` | `historical/release_metadata/EXACT_PERIODS_INVENTORY.json` | 30,889 |
| `/workspace/scratch/196a43c5b4f3/output/PRSC_IX_Reviewed_Completion/MANIFEST.json` | `historical/release_metadata/REVIEWED_COMPLETION_MANIFEST.json` | 26,570 |
| `/workspace/scratch/196a43c5b4f3/review/COMPLETION_REVIEW.json` | `historical/release_metadata/INITIAL_COMPLETION_REVIEW.json` | 2,536 |
| `/workspace/scratch/196a43c5b4f3/review/original_manuscript.txt` | `historical/manuscript/Projector_Resolved_Seed_Calculus_IX_Status_Corrected.extracted.txt` | 84,445 |
| `/workspace/scratch/196a43c5b4f3/edge_recovery/RECOVERED_EDGE_TOWERS.md` | `historical/recovered_source_windows/RECOVERY_REPORT_INITIAL.md` | 6,116 |
| `/workspace/scratch/196a43c5b4f3/edge_recovery/read_0_lines1.txt` | `historical/recovered_source_windows/annals_lines0001_1000.txt` | 29,704 |
| `/workspace/scratch/196a43c5b4f3/edge_recovery/annals_lines1001.txt` | `historical/recovered_source_windows/annals_lines1001_2000.txt` | 21,667 |
| `/workspace/scratch/196a43c5b4f3/edge_recovery/annals_lines2001.txt` | `historical/recovered_source_windows/annals_lines2001_3000.txt` | 25,590 |
| `/workspace/scratch/196a43c5b4f3/edge_recovery/annals_lines3001.txt` | `historical/recovered_source_windows/annals_lines3001_3263.txt` | 11,642 |
| `/workspace/scratch/196a43c5b4f3/edge_recovery/read_1_lines1.txt` | `historical/recovered_source_windows/DEEP_AUDIT_8.retrieved.md` | 3,909 |
| `/workspace/scratch/196a43c5b4f3/edge_recovery/read_2_lines1.txt` | `historical/recovered_source_windows/Euler_Composite_Periodicity_Refined.lines0001_1000.txt` | 41,580 |
| `/workspace/scratch/196a43c5b4f3/edge_recovery/convolution_edge_lines813.txt` | `historical/recovered_source_windows/Euler_Congruences_Convolution_Extension.lines0813_1212.txt` | 13,830 |
| `/workspace/scratch/196a43c5b4f3/least_periods/generic/NewtonDominanceAudit.lean` | `historical/development_audit_drivers/least_periods/NewtonDominanceAudit.lean` | 733 |
| `/workspace/scratch/196a43c5b4f3/strengthening/all_rows/AllRowsAxioms.lean` | `historical/development_audit_drivers/strengthening/AllRowsAxioms.lean` | 2,734 |
| `/workspace/scratch/196a43c5b4f3/strengthening/formalization/DyadicFourSharpeningAudit.lean` | `historical/development_audit_drivers/strengthening/DyadicFourSharpeningAudit.lean` | 1,066 |
| `/workspace/scratch/196a43c5b4f3/strengthening/bridge/BridgeAxiomAudit.lean` | `historical/development_audit_drivers/strengthening/BridgeAxiomAudit.lean` | 1,661 |
| `/workspace/scratch/196a43c5b4f3/strengthening/bridge/bridge_inventory.json` | `historical/development_audit_drivers/strengthening/bridge_inventory.json` | 1,773 |
| `/workspace/scratch/196a43c5b4f3/strengthening/tower/AxiomAudit.lean` | `historical/development_audit_drivers/strengthening/AxiomAudit.lean` | 1,809 |
| `/workspace/scratch/196a43c5b4f3/dyadic_isometry/topology/CompactSelfIsometryAudit.lean` | `historical/development_audit_drivers/isometry/CompactSelfIsometryAudit.lean` | 427 |
| `/workspace/scratch/196a43c5b4f3/dyadic_isometry/topology/DensePadicIsometryAudit.lean` | `historical/development_audit_drivers/isometry/DensePadicIsometryAudit.lean` | 1,389 |
| `/workspace/scratch/196a43c5b4f3/dyadic_isometry/arithmetic/RationalAudit.lean` | `historical/development_audit_drivers/isometry/RationalAudit.lean` | 488 |
| `/workspace/scratch/196a43c5b4f3/dyadic_isometry/controls/DyadicControlsAudit.lean` | `historical/development_audit_drivers/isometry/DyadicControlsAudit.lean` | 532 |
| `/workspace/scratch/196a43c5b4f3/shared_correction/REMAINING_CHECKLIST_DRAFT.md` | `historical/shared_correction_development/REMAINING_CHECKLIST_DRAFT.md` | 13,044 |
| `/workspace/scratch/196a43c5b4f3/shared_correction/core/README.md` | `historical/shared_correction_development/CORE_README.md` | 2,386 |
| `/workspace/scratch/196a43c5b4f3/shared_correction/core/universal_work/SharedUniversal.lean` | `historical/shared_correction_development/universal_work/SharedUniversal.lean` | 3,099 |
| `/workspace/scratch/196a43c5b4f3/shared_correction/core/universal_work/SharedUniversal.log` | `historical/shared_correction_development/universal_work/SharedUniversal.log` | 215 |

## Interpretation and placement

- Files under `historical/` are preserved as history. Their old open/closed statuses do not override the new root checklist. In particular, the initial strengthening notes predate the completed all-row, exact-period and isometry proofs.
- The `SharedUniversal.lean` development source repeats results now merged into the active core. Archive it without adding it to active compilation inventories.
- `native_work/paper_ix.txt` and `review/original_manuscript.txt` are byte-identical. Keep the one extraction listed above. The underlying original status-corrected PDF is already in the baseline ZIP.
- The reconstructed Annals TeX is already present under `strengthening/recovery/`. Its four raw chunks differ from their concatenated reconstruction only by the three inserted boundary blank lines. Including the raw chunks preserves source recovery provenance but does not add a new theorem or full manuscript version.
- The composite-periodicity and convolution-extension source windows are partial. Their original full manuscripts were not materialized here. Do not relabel these windows as complete manuscripts.
- Historical raw sources can contain the historical author name. New release documents should retain `Komorebi P.`; do not silently modify historical source bytes while claiming their original hashes.

## Deliberate exclusions

| Local item | Bytes | Reason |
| --- | ---: | --- |
| `review/Nishibuchi_arxiv_2605.10677v2.pdf` | 398,338 | Third-party primary-source paper. Existing source record intentionally provides version, URL and checksum without redistributing the full paper. |
| `review/Nishibuchi_arxiv_2605.10677v2.txt` | 130,841 | Full third-party text extraction. Keep the existing source record and audit instead. |
| `review/source_page8.png` | 289,054 | Third-party source screenshot used during the existing source audit; not needed to reproduce our proof sources. |
| `review/NISHIBUCHI_SOURCE_RECORD.json` | 1,959 | The staged source record contains all these fields plus the explicit distribution note; do not replace it with this older copy. |
| `edge_recovery/request1.json` | 180,304 | Raw search response includes numerous unrelated Library search results and opaque retrieval metadata. Relevant recovered mathematical text is listed above. |
| `edge_recovery/request2.json` | 167,747 | Same exclusion as request1.json. |
| `native_work/paper_ix.txt` | 84,445 | Exact duplicate of the manuscript extraction listed above. |

Exclude the separate portable Lean/runtime bundle, compilation artifacts and build directories, symlinks, interpreter caches, and repeated copies of earlier cumulative ZIPs. Retain the original baseline ZIP as the existing unique provenance dependency. Historical manifests/inventories from old releases are copied as individual small files.

## Already covered baseline material

The preserved `baseline/PRSC_IX_v0.11.0_Nishibuchi_Completion.zip` is 6,995,942 bytes, SHA-256 `1f02400e73da1d9b6c90a06dcdb5a45c6fd20a4e2addca2a9e638db872cbc721`. It contains the status-corrected Paper IX PDF, Lean sources, earlier block supplements in LaTeX/PDF, ledgers, computational scripts, audits and historical proof provenance. The main original PDF is `paper/Projector_Resolved_Seed_Calculus_IX_Status_Corrected.pdf` within that baseline archive. Its presence does not mean that historical manuscript has been rewritten to include all later continuation theorems.

## Completeness method for final assembly

1. Start from the verified cumulative isometry stage, preserving its proof/audit history and baseline ZIP.
2. Copy every entry in `package_coverage_copies.json` to its listed destination and assert the expected byte length and SHA-256.
3. Add the newly verified polynomial lifting block and preserve the old root README/checklist/release audit/manifest as historical snapshots before updating them.
4. Generate a fresh manifest of every distributed file and explicitly list the baseline ZIP contents or point to its internal manifest. Reject symlinks and build/cache suffixes in the distribution tree.
5. Compare all seven prior output archives by uncompressed-entry SHA-256 against the final tree. With the listed additions, every prior archive entry is covered without nesting all prior ZIPs. Distinguish historical files from the current active verifier input set.
6. Verify ZIP integrity, content count and file hashes after compression. Report completeness as all known local Paper IX proof sources, manuscripts, research checkpoints and audit history covered by this inventory, plus the newly checked block. Do not claim a census of every Paper IX file in remote storage or every historical full manuscript.

## Remaining manuscript limitation

No complete standalone source for the two early recovered edge manuscripts was obtained in this workspace. The Annals paper is available as a reconstructed textual copy, and the original status-corrected Paper IX is available as a PDF in the baseline. The final package can faithfully contain all currently recovered material while explicitly retaining those format and provenance limits.
