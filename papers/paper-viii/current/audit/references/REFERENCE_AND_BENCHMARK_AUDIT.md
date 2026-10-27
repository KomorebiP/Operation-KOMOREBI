# Paper VIII reference and benchmark-contract audit

Checked on 2026-10-06 UTC. This is a read-only review of the strengthened source. Raw sources were not edited. The companion source is an identical inherited copy; it is not independent evidence.

## Bibliography

All 26 keys are cited. A brace-aware local parser found 26 unique records, no missing or uncited keys, and valid DOI syntax wherever a DOI is supplied. BibTeX 0.99d processed the whole database under `plain.bst` with exit code 0 and no warnings. `bibliography_syntax.blg` records the actual syntax gate. The old identifier ledger has a stray leading brace in its displayed NVIDIA/IEEE organization names; the actual double-braced BibTeX organization names are valid.

The external primary-source check is deliberately bounded. `BIBLIOGRAPHY_PRIMARY_SOURCE_SCOPE.json` distinguishes publisher metadata, author-hosted sources, an adjacent preprint, and inaccessible exact records. It does not authenticate all bibliography fields or reprove every classical result. No wrong DOI was established in the checked scope. Classical CG and rounding-result applications were assigned to the separate mathematical auditor.

The NVIDIA record requires a stable locator. The source's unversioned “Version consulted May 2026” is not independently pinned. The official archive at `https://docs.nvidia.com/cuda/archive/12.8.1/cuda-c-programming-guide/index.html#cuda-graphs`, section 3.2.8.7, directly supports separating graph definition, instantiation, and repeated execution. This is CUDA Toolkit archive 12.8.1, accessed 2026-10-06. NVIDIA's release history associates Toolkit 12.8 Update 1 with March 2025; it does not supply the exact guide revision date. Omit the guide's publication year if that date is needed precisely, or label 2025 as the toolkit-release year. Keep the existing cite key for continuity.

Hopkins Press independently supplies DOI `10.56021/9781421407944` for *Matrix Computations*, fourth edition, 2013; adding it is optional. Springer authenticates the mathematical `O(N log N)` title and subtitle of Ambikasaran–Darve; the inherited plain-word title can be restored typographically without changing its identifier. Wickerhauser's author bibliography contains conflicting volume/page metadata for Coifman–Wickerhauser. The exact IEEE page was not accessible enough to adjudicate that conflict. Retain the existing 38(2), 713–718 record rather than silently adopting the contradictory author-list transcription.

## Archived benchmark evidence

The JSON has 154 rows in 16 suites, with 74 CPU and 80 GPU rows. All carry the historical `status=measured` label. No GPU was timed in this review. The archived environment reports an RTX 3070 Ti Laptop GPU, compute capability 8.6, PyTorch 2.11.0+cu128, and seed 20260711; these are recorded metadata, not a current device observation.

The independent standard-library replay reproduced all 486 non-null speedup fields as ratios of archived medians for the same case/output group. This includes baseline identity ratios, so 486 is an arithmetic-check count, not an experiment count. Of these, 246 have an arithmetic-consistent baseline with the same raw timing-scope string, while 240 compare different raw scope strings. These are diagnostics, not a claim that all 246 satisfy the complete fair-match definition. `REFERENCE_AND_CORPUS_REPLAY.json` preserves each compared row and the actual baseline candidates.

The corpus has case IDs, seeds, dimensions, ranks, dtypes, outputs, scopes, warmup/repeat counts, medians and quantiles. It has no source-array fingerprint, correctness-reference identifier, timer implementation, or raw repeat samples. `compile_ms` is non-null in 2 rows, `structure_discovery_ms` in 2, `reuse_count` in 2, `relative_error` in 149, and `residual_error` in 4. The introduction must describe the complete protocol as a requirement; it cannot say this archived corpus records every required field.

The legacy `fairness_violations` function groups by case ID and output contract, then checks that those group fields are constant. This is largely guaranteed by the grouping itself. Its empty result cannot authenticate missing source values, references, timer scope, or actual execution. Seeds and notes provide retained provenance but cannot replace these missing records.

## Material comparisons and required qualifications

| Comparison | Archived ratio or result | Evidence boundary |
|---|---:|---|
| Block width 64, dimension 8192, 32 right sides: GPU dense / GPU packet | 14.8919009493 | Same case/output, float32, and `device_resident` scope. Complete source/reference execution provenance remains unavailable. |
| Same block packet versus CPU dense | 235.7403528302 | CPU `resident` versus GPU `device_resident`; descriptive compute-only cross-device ratio, excluding transfers/setup. |
| Rank-8 BDLR at dimension 8192: GPU dense / graph packet | 10.9354975141 | `device_resident` versus `graph_replay`; graph capture/instantiation excluded, with no measured capture cost or reuse count. |
| Same BDLR graph packet versus CPU dense | 153.6527246659 | Both the processor and scope differ. |
| Two-stream path versus serial two GEMMs | 4.23675 ms versus 3.6556799412 ms | Same two-matrix output, but `device_resident_wall` versus `device_resident`; observed negative comparison, not an identical-scope kernel claim. |
| GPU BDLR materialized products, dimensions 512/1024 | 0.4085760117 / 0.5073439851 ms | Raw notes say factor and expansion times were measured separately and summed. These totals are not medians of independently timed complete workflows. |
| Hidden blocks, dimensions 512/1024 | 26 / 32 uses | Exact strict break-even thresholds for the archived decimal medians; timing uncertainty and another device are not certified. |

The compressed BDLR-product rows correctly have null dense speedups because their output contracts differ. Preserve them as a contract-conversion illustration. The dense FP16/BF16/TF32 frontier is a precision/error tradeoff; it does not isolate processor gain at one common precision. Report all benchmark ratios as retained measurements or descriptive calculations, and reserve “fair match” in the strong formal sense for complete metadata plus identical declared scope.

## Reproduction and scope

Run `python replay_reference_contracts.py --source PATH_TO_STRENGTHENED_SOURCE --output REPORT.json`. The emitted source hashes pin the exact bibliography, manuscript, and benchmark JSON. This script reads archives and checks arithmetic only. It makes no hardware call. The small initial replay failure arose from treating the `cpu_packet` role as a method-name prefix; the historical randomized-SVD role uses a different method name. The corrected replay uses explicit role aliases and records every candidate baseline. No benchmark row was changed.

No novelty search was attempted. Publisher metadata authentication is distinct from theorem extraction and applicability. Missing exact pages and conflicting catalog metadata remain explicit scope limits.
