# Paper XI — continue from Publication Block05

**Current:** P11-PUB-B05. **Next:** P11-PUB-B06. **Ledger:** v0.5.0, 23 stable task IDs.

Read PROGRESS_LEDGER.md / JSON, BLOCK05_REVIEW.md, FAILURES_AND_LIMITATIONS.md, and the plate catalog. Verify before editing. Keep output and logs outside the checkpoint root.

## What changed, and what did not

The new independent visual atlas has 36 pages and 32 worked plates. Its LaTeX, Python figures, exact model data, and four-suite replay runner are editable and rebuilt. The 77-page research reader stays v0.4.0, byte-preserved. The original core monograph / visual / Lean readers remain unchanged at 109 / 51 / 234 pages. Do not give their filenames a new final status merely because they appear in this package.

All 1001 files in baseline/core_readers_editable were copied byte-for-byte from the verified Block01 archive for the next block. They were not rebuilt or fully proofread in B05. The three original wrappers and their hashes are in NEXT_SOURCE_QUEUE.json. The traditional wrapper uses a local fonts/ path and the Lean wrapper a system-font path. Fonts are not bundled. Audit those dependencies in a separate working copy and use locally installed fonts. Do not copy font files into a delivered archive.

## Start B06: synchronize the original readers

1. Read the three original wrappers, their source catalogs, and build drivers. Verify source lineage and locate every include/figure dependency before changing files.
2. Audit the original main reader's current realization/comparison wording against progress-paper Section 1 and the latest ledger. Preserve the proved finite statements. Conjecture 66 is original obligation 66, historical Claim 16.2, and row 95 of the all-records register. Those labels are not interchangeable with record 66.
3. Add a coherent reading route to the separate 77-page progress paper and 36-page atlas. Keep the two companions separate rather than pasting a second copy of every old proof into each reader. Reconcile historical checkpoints without rewriting their evidence dates.
4. Update the original visual and Lean companions' navigation and evidence boundaries. The atlas does not change any theorem binder or supply an existence field. Use the inherited original declaration/source catalogs; do not invent a new theorem count.
5. Rebuild and render the revised originals before a final publication sign-off. Keep proof text and scientific source preservation receipts. The original reader synchronization may take more than one block.

## Mathematical boundaries

The two candidate routes require identification: a source-defined induction candidate is not automatically the direct type-defined candidate. The original theta0 occurrence route is excluded under its hypotheses. The corrected full character passes a scalar test, but occurrence in the same continuation113 candidate remains open.

Preserve full character domains, central normalization, canonical extension and noncompact generator. At rank eight, the full and skipped profiles share conductor 68, torsion 1 and self-pair 342 but have capacity 6 and 4. Equality of those integers is not H5 or native attachment.

The freely transported marking contract is a positive restricted contract. Do not insert a new native-marking premise into it. When an independent native marking is actually prescribed, compute it on the actual candidate: six lift-square bits, represented center, all prescribed section products, actual actions, honest phases and transport maps. The atlas leaves these fields null. Abstract Gauss sums, transvections and odd-action corrections do not supply that certificate.

General realization, same-candidate H5, corrected-character occurrence, and the stronger independently fixed native certificate retain separate ledger tasks. A failed host is not a failure of every permitted host.

## Documentary gaps and checks not run

The complete B02 editable ZIP and successful terminal v0.45 build receipt remain unrecovered. The B04 Henniart–Lemaire full-PDF audit boundary remains inherited. B05 made no new attempt to close those documentary gaps. There was no fresh Lean/Lake compilation, arithmetic matrix-constructor replay, extra seven-program B03 arithmetic replay, new classical-source audit, or external peer review.

## Commands

```text
python tools/verify_package.py
python tools/check_publication.py --output ../b06_precheck/publication.json
python tools/replay_block05.py --output ../b06_precheck/replay
python tools/build_atlas.py --output ../b06_precheck/atlas_build
python tools/compare_pdfs.py publication/pdfs/Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf ../b06_precheck/atlas_build/Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf --output ../b06_precheck/pdf_comparison.json
```

The source checkpoint contains selected historical sources and the entire compact B04 predecessor. The full recovered-source ZIP additionally includes the unchanged complete Block01 archive under historical/. Extract it separately when the larger scientific baseline is needed. This is not the missing complete B02 archive.

Retain all 23 task IDs, append history, keep MD/JSON snapshots, and record each failure or skipped check. Archive-specific delivery receipts are separate to avoid a circular self-hash. No process is left running at delivery.
