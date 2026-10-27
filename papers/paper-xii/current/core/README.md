# Paper XII — reading release 1.0.0
## Patching Support and Hecke Packets
### Conditional automorphic completion

Operation Komorebi · Komorebi P. · 10 October 2026

This is the coordinated, internally reviewed three-reader publication release. It is not a new claim of unrestricted reciprocity, universal companion existence, or a fresh Lean build.

| Reader | Physical PDF pages | Role |
|---|---:|---|
| `publication/pdfs/Paper_XII_Traditional_v1.0.0.pdf` | 40 | Complete retained mathematical manuscript, 18 vector figures, new reading map and contents |
| `publication/pdfs/Paper_XII_Visual_Guide_v1.0.0.pdf` | 28 | Cover plus 27 worked lessons, with restored lesson/page correspondence |
| `publication/pdfs/Paper_XII_Lean_Guide_v1.0.0.pdf` | 31 | Exact source excerpts, all 49 revised claims, complete 96-module catalogue, evidence limits |

Keep the three PDF filenames together. Some PDF viewers disable local-file links. The printed statement numbers and `READING_CONCORDANCE.md` provide a fallback.

The inherited formal contract is 49 revised internal claims, mapped to 291 distinct production targets. The original wording is tracked separately: 41 complete, seven partial, one unchecked. Eight amended statements are not retrospectively counted as proofs of their stronger original formulations. See `RELEASE_SCOPE.md`.

## Start here

Read `RELEASE_REVIEW.md`, `PROGRESS_LEDGER.md`, `FAILURES_AND_LIMITATIONS.md` and `BUILD.md`. `CONTINUE_HERE.md` is the restart point. JSON versions of the ledger and every execution report are included.

The current sources are in `publication/source/`. The complete recovered predecessor is retained in `predecessor/`, except for nine standalone font files deliberately omitted from redistribution. Every retained predecessor file was compared byte-for-byte with the recovered archive. No scientific source or proof was removed. Historical manifests and reports remain historical and are not overwritten. The new root manifest is authoritative for this distribution.

`predecessor/source/` includes the original and native formal archives, exact sources, historical compiler objects and log records. Those records were authenticated, not rerun with Lean. The pinned compiler and dependency cache are not distributed. Follow the Lean guide before any future proof replay, using a separate writable copy.

## Fresh execution

Seven named gates passed: predecessor/source-object integrity, the original 92,892-check finite suite, 31 exact appendix checks, 46 exact visual checks, 3,216 primitive-benchmark assertions, native historical-record authentication, and 26 new publication regression methods. These overlapping finite counts are not added into a theorem total. The authentication gates do not invoke Lean.

All 99 pages were rendered for layout review, with 14 pages inspected individually at 150 dpi. An isolated source copy reproduced the three PDFs and four redrawn figure PDFs byte-for-byte in the checked environment. Archive-specific delivery and fresh-extraction receipts accompany the downloadable release separately, avoiding a circular hash of the archive itself.

## Commands

```text
python tools/verify_package.py
python tools/replay.py --output ../paper_xii_replay
python tools/build_readers.py --output ../paper_xii_build
python tools/audit_publication.py --output ../paper_xii_publication_check.json
```

Write all outputs outside this tree. See `BUILD.md` for prerequisites and evidence scope.
