# Records and review history

Start with the guides below, then open a record for its scope, source revision, environment, and result.

## Current record map

| Question | Current entry point | Structured record |
|---|---|---|
| Which sources are available? | [Component index](COMPONENT_INDEX.md), [source coverage](SOURCE_COVERAGE.md) | [Source index](../manifests/source-components.json), [import receipts](../manifests/source-imports/) |
| What is complete, checked, or still open? | [Status guide](COMPLETION_STATUS.md), [evidence catalogue](STATUS_CATALOG.md) | [Project status](../manifests/project-status.json) |
| What remains to finish? | [Finalization queue](FINALIZATION_QUEUE.md) | Queue entries in [project status](../manifests/project-status.json) |
| How are collection records maintained? | [Maintenance guide and selected cleanup checkpoints](MAINTENANCE.md) | [Git history](https://github.com/KomorebiP/Operation-KOMOREBI/commits/main/) |
| What is publicly distributed? | [Publication status](PUBLICATION_STATUS.md), [distribution notice](DISTRIBUTION_STATUS.md) | [Public publication record](../manifests/release-candidate.json) |
| What did a particular check establish? | [Verification guide](VERIFICATION.md), dated reports below | [Execution evidence](../verification/README.md) |
| What did the earlier collection record? | [Historical snapshots](history/README.md) | [Historical manifests](../manifests/history/) |

The filename `release-candidate.json` is retained for compatibility. Its current status is `PUBLIC_SOURCE_COLLECTION`. It does not mean the public repository is still a private candidate. The earlier private-candidate record has its own historical path.

## Bounded review history

These reports appear in review order, including those written on the same date. Later totals include earlier reviews, so do not add them together. Read each result with its scope, limitations, and source details. Updating this index does not add a review.

| Date | Report | Recorded scope | Evidence binding |
|---|---|---|---|
| 2026-10-27 | [Focused soundness and reader-list review](SOUNDNESS_REVIEW_2026-10-27.md) | Editorial screening of seven entries, three focused claim audits, and two inspections of implementation limits. | [JSON record](../manifests/reader-curation-2026-10-27.json) |
| 2026-10-27 | [SRIC admission audit: three acceptance gaps](SRIC_ADMISSION_AUDIT_2026-10-27.md) | Block 24 Python admission counterexamples and Block 23 documentation scope comparison. | [JSON record](../manifests/sric-admission-review-2026-10-27.json) |
| 2026-10-27 | [SRIC admission repair: runtime 0.3.3](SRIC_REPAIR_2026-10-27.md) | Known admission defects repaired in a separate source edition. Finite qualification only. | [JSON record](../manifests/sric-repair-review-2026-10-27.json) |
| 2026-10-27 | [Machine Societies: three additional proof reviews](MACHINE_SOCIETIES_PROOF_REVIEW_2026-10-27.md) | Three written proofs only: deterministic quotient, erasure reconstruction, and repair budget. | [JSON record](../manifests/machine-societies-review-2026-10-27.json) |
| 2026-10-27 | [Machine Societies: memory, composition, and governance review](MACHINE_SOCIETIES_PROOF_REVIEW_BATCH2_2026-10-27.md) | Eight written statement/proof pairs: identifiability, memory, composition, simulation, symmetry, governance quotient/refinement, and institutional language transport. | [JSON record](../manifests/machine-societies-review-batch2-2026-10-27.json) |
| 2026-10-27 | [Machine Societies: stochastic closure and error bounds](MACHINE_SOCIETIES_PROOF_REVIEW_BATCH3_2026-10-27.md) | Six written statement/proof pairs: controlled lumpability, finite-horizon closure, implementation dependence, transport defects, finite-block averaging, and robust reduced-model enforcement. | [JSON record](../manifests/machine-societies-review-batch3-2026-10-27.json) |
| 2026-10-27 | [Machine Societies: safety, amendment, and computability review](MACHINE_SOCIETIES_PROOF_REVIEW_BATCH4_2026-10-27.md) | Six written statement/proof pairs: inductive safety, finite-horizon viability, amendment confluence, quiescent replication, exclusive service, and the computability boundary. | [JSON record](../manifests/machine-societies-review-batch4-2026-10-27.json) |

## Current written-proof coverage

For [Machine_Societies_v1.0.0.tex](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), the bound records cover **38 of 62 distinct pairs**: 36 recorded passes, 2 requiring restrictions, and 24 unreviewed. [Coverage and exact claim labels](../manifests/machine-societies-review-index.json).

Restrictions and unresolved findings remain in the [component evidence catalogue](STATUS_CATALOG.md) and [finalization queue](FINALIZATION_QUEUE.md). Review coverage is not a correctness percentage, whole-book certification, or independent peer review. The [finalization queue](FINALIZATION_QUEUE.md) records the current maintenance priority. Scheduling does not change these verdicts.

## Other dated reports

- [Repository audit: 27 October 2026](AUDIT_2026-10-27.md)
- [Source inventory reconciliation](SOURCE_INVENTORY_RECONCILIATION_2026-10-27.md)

## Additional registered evidence

These files include test contracts, source records, run outputs, publication receipts, and editorial assessments. Each describes its own purpose and scope.

- [manifests/reader-assessment-2026-10-27.json](../manifests/reader-assessment-2026-10-27.json)
- [verification/constructive-repair/windows-2026-10-27/summary.json](../verification/constructive-repair/windows-2026-10-27/summary.json)
- [verification/constructive-repair/windows-2026-10-27/wheel-source-binding.json](../verification/constructive-repair/windows-2026-10-27/wheel-source-binding.json)
- [verification/publication/2026-10-27.json](../verification/publication/2026-10-27.json)
- [verification/audits/soundness-2026-10-27/contract.json](../verification/audits/soundness-2026-10-27/contract.json)
- [verification/audits/soundness-2026-10-27/run/manifest.json](../verification/audits/soundness-2026-10-27/run/manifest.json)
- [verification/audits/sric-admission-2026-10-27/run/manifest.json](../verification/audits/sric-admission-2026-10-27/run/manifest.json)
- [verification/audits/sric-admission-2026-10-27/contract.json](../verification/audits/sric-admission-2026-10-27/contract.json)
- [packages/sric-admission-v0.3.3/EDITION.json](../packages/sric-admission-v0.3.3/EDITION.json)
- [verification/audits/sric-repair-2026-10-27/run/manifest.json](../verification/audits/sric-repair-2026-10-27/run/manifest.json)
- [verification/audits/sric-repair-2026-10-27/contract.json](../verification/audits/sric-repair-2026-10-27/contract.json)
- [manifests/machine-societies-review-index.json](../manifests/machine-societies-review-index.json)
- [manifests/source-inventory-reconciliation-2026-10-27.json](../manifests/source-inventory-reconciliation-2026-10-27.json)
- [verification/source-publication-2026-10-27.json](../verification/source-publication-2026-10-27.json)
- [manifests/machine-native-reading-edition-2026-10-29.json](../manifests/machine-native-reading-edition-2026-10-29.json)
- [manifests/euler-packets-worked-example-2026-10-29.json](../manifests/euler-packets-worked-example-2026-10-29.json)
- [verification/resolution-semantics/windows-2026-10-30-run5/receipt.json](../verification/resolution-semantics/windows-2026-10-30-run5/receipt.json)
- [verification/constructive-repair/qualified-2026-10-30/summary.json](../verification/constructive-repair/qualified-2026-10-30/summary.json)
- [verification/constructive-repair/qualified-2026-10-30/release-record.json](../verification/constructive-repair/qualified-2026-10-30/release-record.json)
- [verification/constructive-repair/qualified-2026-10-30/qualification-linux-py3135.json](../verification/constructive-repair/qualified-2026-10-30/qualification-linux-py3135.json)
- [verification/constructive-repair/qualified-2026-10-30/qualification-windows-py3135.json](../verification/constructive-repair/qualified-2026-10-30/qualification-windows-py3135.json)
- [verification/resolution-semantics/graphs-windows-2026-11-01-run1/receipt.json](../verification/resolution-semantics/graphs-windows-2026-11-01-run1/receipt.json)
- [verification/resolution-semantics/counting-windows-2026-11-01-run1/receipt.json](../verification/resolution-semantics/counting-windows-2026-11-01-run1/receipt.json)

## Reading and updating a record

1. Identify the component and exact source edition or commit.
2. Read the stated claim or tested input range, environment, outcome, and limitations.
3. Check whether the record describes source identity, compiler acceptance, a written argument, or an experiment. These are different kinds of evidence.
4. Follow a later correction through its own record. Preserve the earlier result and its source binding, including failures and incomplete checks.

The collection workflow validates registered hashes, links, and generated pages. Source integrity and a green workflow do not rerun or certify every scientific claim.

[Documentation](README.md) · [Record formats](../manifests/README.md) · [Preserved history](history/README.md)
