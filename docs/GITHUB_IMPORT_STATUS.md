# GitHub import and qualification status

## Current publication notice

On 27 October 2026, all three canonical repositories became public. The [Realization Calculus publication collection](https://github.com/KomorebiP/Operation-KOMOREBI/releases/tag/papers-2026-10-25) supplies the twelve frozen core-paper archives and additional editions as release assets. The [current publication status](PUBLICATION_STATUS.md) distinguishes those assets, earlier source-tree imports, and pending uploads.

Both independent libraries are **beta releases and works in progress**. Their current sources use Python package version 1.0.0 and C version 0.20.0. The [library guide](LIBRARIES.md) links their current documentation and terms.

The report below is preserved as evidence for **7 October 2026**. Its private visibility, source revisions, qualification results, and remaining-import statements describe that historical checkpoint. They are not assertions about the current publication state.

## Historical import report

Recorded 7 October 2026. All three canonical repositories are private and contain actual source. This is a partial program assembly; further components remain listed in the contribution ledger.

## Imported revisions

| Repository | Exact import or current repair revision | Included scope |
| --- | --- | --- |
| [Operation-KOMOREBI](https://github.com/KomorebiP/Operation-KOMOREBI) | [05399dfff2f86cd319351edd090df2ff3913fe3f](https://github.com/KomorebiP/Operation-KOMOREBI/commit/05399dfff2f86cd319351edd090df2ff3913fe3f) | 2,813 canonical files: Papers I–IV, visual and Lean guides, K-COS, Research Preview 1, readers and source ledger. |
| [komorebi-math](https://github.com/KomorebiP/komorebi-math) | [50447a253c2d00d4a7a4108440e090844b7148b2](https://github.com/KomorebiP/komorebi-math/commit/50447a253c2d00d4a7a4108440e090844b7148b2) | Block 21 source, tests, examples, documentation, compatibility fixtures and subsequent platform fixes. |
| [polyphase-float](https://github.com/KomorebiP/polyphase-float) | [0ec253fd7e0547aac13def718ea19b92787bf36d](https://github.com/KomorebiP/polyphase-float/commit/0ec253fd7e0547aac13def718ea19b92787bf36d) | Version 0.18.0 source, compiled tests and compiler-aware export-audit regression. |

The original central import has tree `02b24ae730f9b1ed81d498bae4080ee972ad8d8e`; it matches the saved canonical Git snapshot exactly, including file modes. The original Math import has tree `60561e59df85f328d00220570abd74e9f8b12c39` and [commit 192e78db394ffe4ebc74d713c38bf3b877030dd4](https://github.com/KomorebiP/komorebi-math/commit/192e78db394ffe4ebc74d713c38bf3b877030dd4). Subsequent Math changes have tree `faf5d17d4ab43090ab02bb4b2b53d2d5b87f2081`. The navigation updates and local validation receipts accompanying this status are additions to the central import.

## Fresh verification

The [central collection and artifact workflow](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/37697917528) passed on the original import. Local checks passed all five preserved paper import manifests, covering 2,573 files, 43 receipt/upload tests, seven diagnostic tests and 768 exact coefficient comparisons. Maintained navigation passed 118 local links. Paper IV's bounded replay passed 818 numeric rows and four rational cubic brackets, and resolved 1,164 formal target records. Full local receipts and their logs are in [verification/github-import-2026-10-07](../verification/github-import-2026-10-07/central/CENTRAL_REPOSITORY_VALIDATION.json).

The [current Math qualification](https://github.com/KomorebiP/komorebi-math/actions/runs/37698654422) checks Linux and Windows on Python 3.11, 3.12 and 3.13, strict documentation, reproducible distributions, and dependency-isolated installed wheel and rebuilt source-distribution tests. All eight jobs passed: the six Linux/Windows Python jobs, strict documentation, and isolated distribution qualification. Windows Python 3.13 reported 1,723 passed and nine skipped tests. The [workflow receipt](../verification/github-import-2026-10-07/WORKFLOW_RECEIPT.json) records all terminal outcomes and exact revisions.

Polyphase's [CI](https://github.com/KomorebiP/polyphase-float/actions/runs/37698068776) and [ABI governance](https://github.com/KomorebiP/polyphase-float/actions/runs/37698068539) passed on the current repair revision. The [CodeQL workflow](https://github.com/KomorebiP/polyphase-float/actions/runs/37698068577) passed and retained the 42,791-byte SARIF artifact for review in private staging; its artifact identity is recorded in the workflow receipt. Analysis execution is distinct from a claim of no findings.

Lean sources and historical proof receipts are retained. Fresh Lean compilation was not run in this import pass. These artifact checks and bounded computations do not replace theorem replay or complete corpus reconciliation.

## Failures found and repairs

- The candidate ZIP omitted Paper II's 415-byte requirements.lock. The exact file was restored from the canonical Git bundle and its recorded hash verified. The uploaded canonical tree includes it.
- ZIP extraction also lost executable launcher modes. The canonical Git snapshot retained all 24 Math launcher modes at 100755; the restored working copy matched those modes.
- Two Math dependency-download commands were invalid YAML because the unquoted `--only-binary=:all:` argument contains a colon followed by a space. Block scalars preserve the commands and parse correctly.
- Windows-generated wheel metadata uses CRLF. The builder now parses the unique Version header instead of requiring an LF-only substring; malformed, missing and duplicate identities still fail.
- Python 3.11 reflects the inherited EnumType constructor differently. The compatibility audit normalizes only the ordinary stdlib metaclass, preserving explicit and custom-metaclass signatures and unchanged public/stable API digests.
- A release-test fixture read a UTF-8 README through the Windows default encoding. Its reads and serialization now use explicit UTF-8; a CP1252-default regression reproduces the original failure and verifies the fix. Production identity checks were unchanged.
- Clang omits GCC-only decimal exports. The Polyphase audit checks existing build-feature probes and still rejects missing enabled symbols, unexpected symbols and invalid probes. Twenty-two ELF fixture cases passed locally, and the new CTest regression passed on hosted GCC and Clang builds.
- Code Scanning uploads failed in private staging. CodeQL queries remain enabled; private runs save SARIF artifacts and public runs retain Code Scanning uploads.

Selected local repair receipts are preserved beside the central validation receipts. Source and workflow repairs have focused regression tests; no mathematical claim or distribution license was changed.

## Remaining assembly

Papers V–XII, Stratified Universality, Signal Reconstruction, OSL/Neuralese and later program components still need their selected sources imported and reconciled. The historical 87-record register remains a source-reconciliation baseline, not a current theorem count. The exact October Paper X companion-source gap remains visible in the selection record.

All component-specific terms remain in place. This private import does not change repository visibility, publish a release, or grant a new license.

