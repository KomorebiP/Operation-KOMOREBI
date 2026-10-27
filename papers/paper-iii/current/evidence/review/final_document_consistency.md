# Final active-document consistency review

**Review date:** 20 October 2026. **Source binding:** approximately 14:32 UTC, reconfirmed with the final PDFs at 14:34 UTC. **Verdict:** PASS for the corrected active-document revisions and final PDF text/hash checks below. Both required consistency corrections were applied and re-read; no other required correction was identified.

This was a read-only review of release language, counting units, current-versus-preserved scope, reproduction descriptions, and licensing statements. It did not rerun mathematics, computation, Lean, or visual layout QA. Checkpoint and provenance documents were excluded, as was `RELEASE_STATUS.json`, which the release editor was replacing. References to preserved records were checked only for clear separation from current claims.

## Required corrections, now resolved

1. **Lean guide scope:** `guides/lean/chapters/01_orientation.tex` formerly said that no fresh compiler run was claimed by the guide. The sentence appeared in the then-current standalone guide on physical page 8 and combined reader on physical page 141, contradicting the new release chapter. The corrected source limits the static checks to preserved evidence and separately identifies the current compiler and replay runs. Its opening paragraph and map description now explicitly concern the preserved finite predecessor, so the seven-module and 41-row descriptions cannot be mistaken for the current closure.
2. **Shipped build files:** `formal/README.md` formerly said that build outputs were not bundled. Its corrected ending distinguishes the predecessor's omission from the current release, which retains owned generated objects while excluding the compiler and upstream dependency caches. This now agrees with the root README, reproduction instructions, and actual `formal/build/final_objects/` contents.

These are documentation corrections; no mathematical or formal source was edited in this review. PDF text inspection located the first issue. After the final rebuild, the corrected wording was independently confirmed in the actual PDFs at the hashes below. This text/hash check is separate from the release's rendering and layout QA.

## Consistency findings

- Current formal counts agree: **16 production modules; 608 owned declarations; 594 replayed logical declarations; 14 separately inventoried runtime helpers; 33 owned declarations outside the main namespace; 14 accepted control commands**. The 330 theorem-kind entries are correctly distinguished from numbered manuscript results. The declaration-kind totals and replay-plus-helper totals equal 608.
- The manuscript census remains **167 numbered environments**, including **98 non-standard result environments and two classical standard facts**. These units are explicitly different from compiler declarations. The current exact-computation totals are consistently **15,331 + 2,622 + 677 = 18,630**, with **124 visual checks and four rejected false controls** recorded separately.
- No current compilation blocker remains asserted. References to the two formerly uncompiled candidate modules describe resolved failures. The preserved finite counts are identified as historical. The Lake project version `1.0.1` matches `formal/lakefile.toml`; it is a different versioning unit from technical release `1.0.0`.
- No reviewed document claims full Lean formalization of the monograph. Actual range jets, inherited norms, derivative reconstruction, composition hypotheses and one-way support are consistently scoped. Taylor/remainder, the Stirling count, separate norm corollaries and the expanded later formalization retain their declared boundaries. No differentiability claim is inferred merely from the total `iteratedFDeriv` reconstruction.
- Reproduction descriptions consistently distinguish an empty owned object directory for a new cold build from shipped generated objects. They retain the exact compiler and dependency pins and distinguish a PDF rebuild from mathematical-evidence regeneration.
- Rights statements agree with `metadata/LICENSING.md`: no new project-wide public reuse license is assigned, existing notices are preserved, and technical closeout is not represented as a public publishing action.

## Exact reviewed source revisions

All paths below are relative to `paper3_release/`. SHA-256 values identify the bytes reviewed; they do not claim coverage of later edits.

| File | SHA-256 |
|---|---|
| `README_FIRST.md` | `2d3b0ddfe6e626cee5ada7855f7fead49283b44f35df5d0c094cf64e7420010b` |
| `CONTINUE_HERE.md` | `91267225a246985329f74539278807d434aa0bd0870b6f1d30a2bd7f1f50b136` |
| `metadata/RELEASE_NOTES_v1.0.0.md` | `168bd5063315e77419b226638d1bf20e5fed9b2d8a106a2869706ae10264c315` |
| `metadata/FAILURES_AND_LIMITATIONS.md` | `841e0108f1aa820456d5ca57010af7551859a053fd1cd9e1e66c3a53eb2ef17f` |
| `metadata/REPRODUCTION.md` | `5fd372e35de80f647dc87dbc0236163d76313b6419c7f425436f2333eb9898e5` |
| `formal/README.md` | `67215d7734b8556647db7ae7ecf090a6f3a043ff101bcf23e68645644233f521` |
| `formal/README_CONTINUATION.md` | `4267beef80956b5cffb2886811805b2ce5cd8293789b518ebd2f8efa642695b8` |
| `guides/lean/chapters/00_current_release.tex` | `b1d5e82ed220632f1a7dfcab151577895159c7a500cb5c569f0a5dba070acbc8` |
| `guides/lean/chapters/01_orientation.tex` | `65e1dfb7144241933ba3760b213b5bbbf330e79c6c61f709af756eb51eba84b2` |
| `guides/lean/generated/current_receipts.tex` | `e2206d8f904228de2c15b0fcaecd0f18ddc485ffdc07614deb12d80a1134a63a` |
| `metadata/LICENSING.md` | `8076b2bcc0769c3a6da4f62e4cd3c4385bafa35741653bbedc6836bc543c0a6d` |
| `formal/verification/FINAL_VERIFICATION_SUMMARY.json` | `4fa5e0d2dc4a985e5daab29a4b2a6bc17c4dc2300f5552fc64226c72d1d1e24e` |

## Final PDF binding

The corrected orientation appears on physical page **8** of the final Lean guide and physical page **141** of the final combined reader. Both PDFs now identify the preserved finite predecessor, its seven mathematical modules, and the current compiler/replay evidence separately. The former blanket denial of a fresh compiler run is absent from all six current PDFs. The main, Lean-guide and combined-reader hashes were independently computed and match the final build hashes supplied by the release editor. All twelve source hashes above were checked again and still matched after the rebuild.

| PDF under `publication/` | Pages | SHA-256 |
|---|---:|---|
| `Paper_III_Final_v1.0.0.pdf` | 99 | `fb5d7a81487ef1e37bb4aa8fed12bd4cce9b6d9b2df667429173ed8299e8db77` |
| `Paper_III_Analytic_Supplement_v1.0.0.pdf` | 6 | `6df3c0be4e11c786c02daf09c2755cb4fa3f1749f8a78110ac44970569c1090a` |
| `Paper_III_Visual_Guide_v1.0.0.pdf` | 26 | `6d7b928a15f71dfd77ed12f8bb7039ce2407792c523a25034cf170c40965a5f2` |
| `Paper_III_Lean_Guide_v1.0.0.pdf` | 53 | `4dcd44d8b79148db0fd24e2a99a5774ec65e75aa98b52017ba7c7e99b9267028` |
| `Paper_III_Release_Record_v1.0.0.pdf` | 2 | `b64aa368894c4c33e4cdd33b330e28b167cb7de851eb72b9cdc57a967aafe7f6` |
| `Paper_III_Complete_Reading_Edition_v1.0.0.pdf` | 186 | `4c2ae3031ace2dafc48bc1dae4b21ad1795b05311c698ad9b4aa8e149356afa4` |

The component page counts sum to the combined reader's 186 pages. No fresh mathematical validation or visual inspection of the final figure breaks is implied by these document-consistency checks.
