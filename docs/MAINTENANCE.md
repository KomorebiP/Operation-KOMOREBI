# Repository maintenance

Current priority: navigation, record consistency, reproducibility instructions, and collection tooling. Further proof reviews are deferred. Existing findings and completion gates remain in the [finalization queue](FINALIZATION_QUEUE.md).

## Choose the right tool

Run commands from the collection root. The [verification guide](VERIFICATION.md) gives the routine check sequence and checkout requirements. These collection tools use Python's standard library and, where they inspect source history, Git. Individual software packages have separate dependencies.

| Tool | Purpose | File or publication effects |
|---|---|---|
| [check_repository.py](../tools/check_repository.py) | Check entry points, imported contribution paths, and the preserved preview's artifact checker. | Reads the checkout and runs the preview checker. Reports JSON and exits nonzero when prerequisites or checks fail. No Lean execution. |
| [check_source_receipts.py](../tools/check_source_receipts.py) | Compare every selected source receipt with a committed tree; `--revision` selects the tree. | Reads Git objects. Does not write source or qualify uncommitted edits. Git may retrieve missing objects in a partial clone. |
| [update_completion_status.py](../tools/update_completion_status.py) | Validate evidence bindings and regenerate all maintained navigation/status pages. | Writes generated Markdown by default. `--check` validates without rewriting those pages. Both modes read Git history. |
| [update_source_navigation.py](../tools/update_source_navigation.py) | Reconcile source availability after an import, using declared receipts and local source bytes. | Writes a navigation/manifest overlay to the required `--output-root`. Includes availability and contribution records. No commit or push. |
| [update_publication_metadata.py](../tools/update_publication_metadata.py) | Prepare publication metadata from an already validated source index and explicit source commit. | Writes current and historical publication records to the required `--output-root`. Checks metadata consistency; does not independently verify source bytes or query current library releases. |
| [import_source_collection.py](../tools/import_source_collection.py) | Prepare or import a declared source component or batch. | May download archives and extract files. `--prepare-component` writes to `--output`; batch preparation without `--publish` uses temporary files. `--publish` installs sources and receipts, commits, and pushes the configured batch. |

For routine wording or navigation changes, edit the relevant template or maintained document, then use `update_completion_status.py`. The source-navigation and publication-metadata scripts are for source/publication reconciliation; their dated inputs need explicit review before reuse. Use a separate output directory to inspect their overlays before applying them.

The [browse-resource registry](../manifests/browse-resources.json) selects direct reading, text, Lean, and code links for every primary component. [browse_navigation.py](../tools/browse_navigation.py) validates each selection against that component's import receipt and the committed tree, then generates the [browse hub](BROWSE.md) and its category/resource pages. Add or revise explicit selections when an edition changes; file names alone must not promote a scientific status. PDF guides are kept separate from actual Lean files. Incubator entries retain their placement.

[record_navigation.py](../tools/record_navigation.py) and [proof_review_coverage.py](../tools/proof_review_coverage.py) are supporting modules called by the status tool. The latter validates existing claim/evidence bindings; running the status tool does not perform a new proof review. The `test_*.py` files are the collection tooling regression suite. The [workflow guide](WORKFLOWS.md) describes which commands GitHub runs and which workflows can publish.

## Keep records traceable

| Record type | Update rule |
|---|---|
| Current guidance and generated indexes | Edit their source document, template, or registry; regenerate and review the diff. |
| Completion, Lean coverage, or confidence | Change only with supporting evidence for the exact component and edition. A scheduling decision does not change these labels. |
| Dated execution, review, or import record | Retain its original source revision, inputs, result, and limitations. Give a later correction its own record and reference the earlier one. |
| Preserved manuscript or software edition | Introduce an identified corrected edition with source correspondence. Keep the original edition and its evidence accessible. |
| Historical collection snapshot | Keep its date and provenance. Link readers to the current guide when an old statement has been superseded. |

Use the [records guide](RECORDS.md) to locate the current entry point and dated evidence. A source receipt, test result, and written review establish different things. Keep setup failures, skipped checks, and scientific findings distinct.

## Selected published cleanup checkpoints

These entries record two completed documentation/tooling updates from 27 October 2026. They are a bounded maintenance history; the [Git history](https://github.com/KomorebiP/Operation-KOMOREBI/commits/main/) contains subsequent changes. Neither checkpoint adds a mathematical review or changes scientific status.

| Commit | Cleanup | Recorded checks |
|---|---|---|
| [f76b25c](https://github.com/KomorebiP/Operation-KOMOREBI/commit/f76b25c79978549b1725ff23c28b70f1ba931a63) | Added documentation, records, manifest, verification, and history indexes; preserved the older distribution page; clarified the active maintenance priority. | 41 local tooling tests; [collection workflow passed](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/40616404760). |
| [543aed7](https://github.com/KomorebiP/Operation-KOMOREBI/commit/543aed7155f1c0d2ebd3dd6cccfa0a4e4f86d0f8) | Added contribution/citation guidance, report templates, workflow documentation, and checks for registered guides. | 44 local tooling tests; [collection workflow passed](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/40618882704). |

The linked workflow results belong to those commits. A later green run does not replace an earlier receipt or expand its scientific scope.

[Contributing](../CONTRIBUTING.md) · [Run and verify](VERIFICATION.md) · [Documentation](README.md)
