# Collection manifests

These JSON files record available sources, editorial status, and the evidence attached to each edition. Start with the [records guide](../docs/RECORDS.md) for readable reports and their exact companion records.

| File or directory | Role |
|---|---|
| [source-collection.json](source-collection.json) | Selected component declarations and expected source identities. |
| [source-components.json](source-components.json) | Receipt-derived availability and primary/supporting classifications. |
| [browse-resources.json](browse-resources.json) | Selected file and directory shortcuts for each primary work, checked against its source receipt. |
| [source-imports/](source-imports/) | Per-component paths, file hashes, modes, and source provenance. |
| [source-coverage.json](source-coverage.json) | Crosswalk from named inventory entries to available sources and remaining availability limits. |
| [project-status.json](project-status.json) | Completion, Lean, confidence, scope, finalization queue, and registered evidence. |
| [contributions.json](contributions.json) | Historical contributions and current source bindings. |
| [release-candidate.json](release-candidate.json) | Current publication record. The earlier filename is retained for compatibility. |
| [machine-societies-review-index.json](machine-societies-review-index.json) | Unique claim coverage bound to exact manuscript and review hashes. |
| [history/](history/) | Earlier collection snapshots, with their original dates and meanings. |

Dated assessment and review records are indexed in the [records guide](../docs/RECORDS.md). A source receipt identifies the available files. It does not establish scientific completion. Editing a JSON status without the corresponding evidence does not close a finalization gate.

For a maintained status or navigation change, follow [Maintaining reader pages](../docs/VERIFICATION.md#maintaining-reader-pages). Corrections to source or dated evidence need an identified new edition or record and updated bindings.

[Collection](../README.md) · [Documentation](../docs/README.md) · [Execution evidence](../verification/README.md)
