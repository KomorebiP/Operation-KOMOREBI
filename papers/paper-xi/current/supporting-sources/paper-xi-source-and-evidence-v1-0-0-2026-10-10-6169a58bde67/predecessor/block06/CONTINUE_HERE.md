# Paper XI — continue from Publication Block 06

**Current:** P11-PUB-B06. **Next:** P11-PUB-B07. **Ledger:** v0.6.0 with 23 stable task IDs.

## Start here

Read the ledger, BLOCK06_REVIEW.md, FAILURES_AND_LIMITATIONS.md and evidence/block06/SOURCE_CHANGES.md. Run the strict integrity check before editing. All outputs stay outside the checkpoint directory.

```text
python tools/verify_package.py
python tools/replay_block06.py --output ../paper_xi_b07_precheck
```

The original reader trio is now synchronized at v0.6.0: monograph 109 pages, core visual guide 53 pages, Lean/evidence guide 235 pages. The research paper is still the unchanged 77-page v0.4.0 PDF; the independent atlas is still the unchanged 36-page v0.5.0 PDF. These five PDFs together have 510 pages. Do not increment preserved research versions merely to match the package version.

## Best next direction: final release audit

The next block should close the editorial release contract rather than expand open arithmetic research. Audit the five readers' claim wording, references, historical/current labels and reading routes as one set. Check that all delivered filenames, source paths, source hashes, review dates and documented evidence gaps agree. In particular, inspect the manuscript's retained Markdown-derived appendices for any further conversion loss, rather than treating this block's byte preservation as proof that the original conversion was perfect. Their plain source-style notation is intentionally retained in B06 except for the demonstrated missing factor.

The principal same-candidate contract is monograph Section 16.1. Conjecture 66 is historical obligation 66 / historical Theorem 16.2 / all-records row 95, not register row 66. The conditional comparison has its own statement and requires H5 for that same realizer. The core visual guide's lessons 43–45 and the Lean guide's existence-field chapter must remain aligned with it.

Use the current builders and actual source catalogs. Do not overwrite historical review reports with current dates. The modified reader wrappers are under publication/source. All baseline reader files remain under predecessor/block05/baseline/core_readers_editable. The exact patch and preservation report are under evidence/block06. The 68 main proof bodies and 105 main statement bodies are unchanged. Appendix D contains the one documented raw-source-backed dimension restoration.

After any further edit, rebuild the original trio together so its external links use the new actual destinations. Re-render all changed pages, recheck the full link graph, and compare proof/source bytes. The synchronized originals have 107 registered cross-document route IDs with 108 link annotation instances. The unchanged atlas adds its own 32 links. The full five-reader graph currently has 504 internal links and 140 companion links.

The final release may accurately publish a complete reader package about partial mathematical progress. It must not claim a proof of the general conjecture, a new Lean acceptance, or a fully source-rebuilt Block 02 reader unless those tasks actually occur.

## Exact build/review commands

```text
python tools/build_readers.py --output ../paper_xi_b07_build
python tools/render_readers.py --kind Traditional --output ../paper_xi_b07_render
python tools/render_readers.py --kind Visual_Guide --output ../paper_xi_b07_render
python tools/render_readers.py --kind Lean_Guide --output ../paper_xi_b07_render
```

The stage option in BUILD.md supports bounded separate calls. Installed fonts are dependencies, not distributable package files. The current original-reader build is byte-reproducible in the checked environment. Fifty-five monograph underfull-spacing diagnostics and the visual build's safe shell-escape warning remain documented. No overfull boxes, missing references or missing glyphs remain in the checked output.

## Keep these tasks separate

General realization, H5, corrected full-character occurrence, and the independently required native-marking certificate retain their four open ledger entries. The six native square bits, full section products and honest phases were not computed. Do not insert that stronger native requirement into the different transported-marking result.

The full Block 02 source ZIP and successful terminal v0.45 receipt remain unrecovered. Detailed Henniart–Lemaire primary-text input status remains inherited. This block did not invoke Lean/Lake or the direct arithmetic matrix programs. The compact package contains the complete B05 compact predecessor. The full recovered-source package additionally contains the unchanged complete Block 01 archive under historical/, not a replacement for missing Block 02 sources.

Retain all 23 IDs and all prior history entries. Append a checkpoint entry, keep dated Markdown/JSON snapshots, and record failures and skipped checks. No process is running after this handoff.
