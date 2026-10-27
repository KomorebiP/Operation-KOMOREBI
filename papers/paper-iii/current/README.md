# Projector Resolved Seed Calculus III

Komorebi P.

Start with the [complete reading edition](publication/Paper_III_Complete_Reading_Edition_v1.0.0.pdf). It combines the following five components, with bookmarks, internal links and page labels:

| Component | Pages |
|---|---:|
| [Release record](publication/Paper_III_Release_Record_v1.0.0.pdf) | 2 |
| [Mathematical manuscript](publication/Paper_III_Final_v1.0.0.pdf) | 99 |
| [Analytic supplement](publication/Paper_III_Analytic_Supplement_v1.0.0.pdf) | 6 |
| [Visual guide](publication/Paper_III_Visual_Guide_v1.0.0.pdf) | 26 |
| [Lean guide](publication/Paper_III_Lean_Guide_v1.0.0.pdf) | 53 |
| Total distinct component pages | 186 |

The combined PDF repeats these components, so it adds no new content pages to that total. [START_HERE.html](START_HERE.html) provides the reading index.

## Mathematical and formal scope

The corrected manuscript retains its reviewed ordinary proofs under their stated hypotheses. The main paper has 167 numbered environments, including 98 theorem/proposition/lemma/corollary environments and two classical standard facts. Those source counts are separate from compiler declaration counts.

The accepted formal core has sixteen production modules, 608 owned declarations and 594 replayed logical declarations. Fourteen runtime helpers are separately inventoried; fourteen designated control commands passed. Its October 20 build, audit, replay and controls are preserved in [formal/verification/FINAL_VERIFICATION_SUMMARY.json](formal/verification/FINAL_VERIFICATION_SUMMARY.json).

Full Lean formalization of the expanded monograph remains incomplete. The packet Taylor integral remainder and estimate, Stirling/Touchard count, separate restricted-product/Hilbert corollaries and later expanded material retain their ordinary-proof status. The unrecovered historical 2,693-declaration/full-98+2 claim remains uncertified. This freeze does not promote it.

## Complete source and evidence

- [Active manuscript and figures](manuscript/)
- [Guides](guides/) and [analytic supplement sources](docs/)
- [Current formal source and reproduction](formal/README_CONTINUATION.md)
- [Statement register](metadata/MANUSCRIPT_STATEMENT_REGISTER_v1.0.0.json)
- [Release status](RELEASE_STATUS.json), [freeze record](FREEZE_RECORD.json) and [progress ledger](PROGRESS_LEDGER.md)
- [Unchanged prior checkpoint](checkpoint_v0.3.0/) and [earlier source evidence](provenance/)

## Verify and reproduce

Extract this single complete ZIP, enter its root directory and run:

```sh
python3 scripts/verify_frozen_release.py
```

This portable standard-library command checks the exact file set, sizes, SHA-256 values and preservation of every baseline file. The root `MANIFEST_SHA256.json` covers the current frozen package. The original `MANIFEST_SHA256_v1.0.0.json` remains unchanged as a baseline record. Administrative originals are retained under `verification/freeze_2026-10-20/before/`.

`python3 VERIFY_RELEASE.py --pdf` additionally checks the recorded source/evidence bindings and parses PDF links using PyMuPDF. Its current manifest adapter is administrative; the earlier command is preserved with the baseline records. Write optional receipts outside the frozen tree.

Fresh freeze checks authenticate sources, evidence and readers and verify clean extraction. The accepted formal and finite computations retain their October 20 execution records. This freeze does not repeat Lean, experiments, TeX builds or a whole-paper proof audit. Rebuild in a separate working copy using [metadata/REPRODUCTION.md](metadata/REPRODUCTION.md). The pinned runtime, dependency cache and installed fonts remain external prerequisites.

## Open use

Original software and machine-readable material use MIT. Original papers, guides, figures and explanatory writing use CC BY 4.0. See [LICENSE.md](LICENSE.md), [LICENSE_STATUS.json](LICENSE_STATUS.json) and [LICENSES/](LICENSES/) for the current grant and third-party exceptions.

The current author-confirmed grant supersedes older unassigned-license statements, including those in the unchanged PDF release record. Scientific source, reader PDFs and earlier evidence retain their accepted bytes. The publication edition is 1.0.0; this distribution was frozen on October 20, 2026.
