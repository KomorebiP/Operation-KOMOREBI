# Repository maintenance

Current priority: navigation, record consistency, reproducibility instructions, and collection tooling. Further proof reviews are deferred. Existing findings and completion gates remain in the [finalization queue](FINALIZATION_QUEUE.md).

## Choose the right tool

Run commands from the collection root. The [verification guide](VERIFICATION.md) gives the routine check sequence and checkout requirements. Navigation and record tools use Python's standard library and Git where they inspect source history. Package build and qualification tools document their additional requirements.

| Tool | Purpose | File or publication effects |
|---|---|---|
| [check_repository.py](../tools/check_repository.py) | Check entry points, imported contribution paths, and the preserved preview's artifact checker. | Reads the checkout and runs the preview checker. Reports JSON and exits nonzero when prerequisites or checks fail. No Lean execution. |
| [check_source_receipts.py](../tools/check_source_receipts.py) | Compare every selected source receipt with a committed tree. Use `--revision` to select the tree. | Reads Git objects. Does not write source or qualify uncommitted edits. Git may retrieve missing objects in a partial clone. |
| [update_completion_status.py](../tools/update_completion_status.py) | Validate evidence bindings and regenerate all maintained navigation/status pages. | Writes generated Markdown by default. `--check` validates without rewriting those pages. Both modes read Git history. |
| [update_source_navigation.py](../tools/update_source_navigation.py) | Reconcile source availability after an import, using declared receipts and local source bytes. | Writes a navigation/manifest overlay to the required `--output-root`. Includes availability and contribution records. No commit or push. |
| [update_publication_metadata.py](../tools/update_publication_metadata.py) | Prepare publication metadata from an already validated source index and explicit source commit. | Writes current and historical publication records to the required `--output-root`. Checks metadata consistency. Does not independently verify source bytes or query current library releases. |
| [constructive_repair_release.py](../tools/constructive_repair_release.py) | Build and qualify Constructive Repair, verify a prepared archive, or assemble the two accepted platform distributions. Qualification uses pinned setuptools 84.1.0 and wheel 0.48.0. | Writes a new output directory and qualified artifacts. `verify` reads a distribution. The named release workflow performs publication after the two-platform gate passes. |
| [import_source_collection.py](../tools/import_source_collection.py) | Prepare or import a declared source component or batch. | May download archives and extract files. `--prepare-component` writes to `--output`. Batch preparation without `--publish` uses temporary files. `--publish` installs sources and receipts, commits, and pushes the configured batch. |

For routine wording or navigation changes, edit the relevant template or maintained document, then use `update_completion_status.py`. The source-navigation and publication-metadata scripts reconcile source and publication records. Review their dated inputs before reuse. Use a separate output directory to inspect their overlays before applying them.

Library observations are kept in `LIBRARIES` in [update_publication_metadata.py](../tools/update_publication_metadata.py). The qualification page, publication metadata, and contribution ledger use those same observations. Before updating them, inspect each repository's branch commit, workflow result and run commit, and release-tag commit. Record the observation date. A passing run must match the checked source revision. Keep the release-tag commit separate when the tag points to an earlier edition. These local tools validate the recorded identities and do not query GitHub for newer results.

The [browse-resource registry](../manifests/browse-resources.json) selects direct reading, text, Lean, and code links for every primary component. [browse_navigation.py](../tools/browse_navigation.py) validates each selection against that component's import receipt and the committed tree, then generates the [browse hub](BROWSE.md), category/resource finders, and individual work pages in `docs/works/`. Update the selected links when an edition changes. File names alone do not justify a change in scientific status. PDF guides are kept separate from actual Lean files. Incubator entries retain their placement.

Each work page has Read, Written proofs, Lean, Code, and Evidence sections, return links, and previous/next links within its collection. The evidence catalogue links back to that work. Older category anchors remain available. To change a generated navigation page, edit the renderer or resource registry and regenerate the page. Work pages and resource finders use headings and single-column lists to remain readable in narrow panes.

Resource finders have stable component anchors and title shortcuts within each collection. Work sections link to their exact finder entry, which links back to the corresponding section. Generate both links together. Only link to a finder when it has a matching resource. A formal setup document alone must not put a work in the Lean-source finder.

The `lean_setup` resource kind identifies text instructions, source maps, or replay prerequisites. It is separate from `.lean` source and PDF guides. Prefer a small mathematical-module directory or a documented package interface as the first source shortcut. Retain wider project/ancestry links when needed, and label historical checkpoint instructions explicitly. Each new selection still needs ownership and committed-path validation. Reading a setup guide does not execute its commands.

The renderer also records the maintained SRIC 0.3.3 correction as the first code route, with a link to its existing repair report. The original imported code stays linked and is labeled as the preserved edition. Its import receipt remains unchanged.

[navigation_links.py](../tools/navigation_links.py) checks inline relative Markdown links against case-sensitive file and directory paths and validates fragments in maintained/generated pages. It ignores fenced and inline code examples, handles encoded file names and repeated heading IDs, and rejects duplicate explicit anchors. The status command reports checked links/fragments and separately counts remote links and original-source fragments that it does not validate. This is a navigation check, not a full Markdown parser, HTTP availability scan, or PDF accessibility audit.

[record_navigation.py](../tools/record_navigation.py) and [proof_review_coverage.py](../tools/proof_review_coverage.py) are supporting modules called by the status tool. The latter checks the links between existing claims and evidence. Running the status tool does not perform a new proof review. The `test_*.py` files are the collection tooling regression suite. The [workflow guide](WORKFLOWS.md) describes which commands GitHub runs and which workflows can publish.

## Keep records traceable

| Record type | Update rule |
|---|---|
| Current guidance and generated indexes | Edit their source document, template, or registry, then regenerate and review the diff. |
| Completion, Lean coverage, or confidence | Change only with supporting evidence for the exact component and edition. A scheduling decision does not change these labels. |
| Dated execution, review, or import record | Retain its original source revision, inputs, result, and limitations. Give a later correction its own record and reference the earlier one. |
| Preserved manuscript or software edition | Introduce an identified corrected edition with source correspondence. Keep the original edition and its evidence accessible. |
| Historical collection snapshot | Keep its date and provenance. Link readers to the current guide when an old statement has been superseded. |

Use the [records guide](RECORDS.md) to locate the current entry point and dated evidence. A source receipt, test result, and written review establish different things. Keep setup failures, skipped checks, and scientific findings distinct.

## Selected published cleanup checkpoints

The [reader website guide](READER_SITE.md) documents the shared HTML site,
reading ZIPs, claim locations, library pins and publication workflow. Update
the reader registry and templates alongside generated pages. Keep the
accessibility limitations and the scope of transcribed claim links explicit.

These entries record two completed documentation/tooling updates from 27 October 2026. For later changes, see the [Git history](https://github.com/KomorebiP/Operation-KOMOREBI/commits/main/). Neither checkpoint adds a mathematical review or changes scientific status.

| Commit | Cleanup | Recorded checks |
|---|---|---|
| [f76b25c](https://github.com/KomorebiP/Operation-KOMOREBI/commit/f76b25c79978549b1725ff23c28b70f1ba931a63) | Added documentation, records, manifest, verification, and history indexes, preserved the older distribution page, and clarified the maintenance priority. | 41 local tooling tests. [Collection workflow passed](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/40616404760). |
| [543aed7](https://github.com/KomorebiP/Operation-KOMOREBI/commit/543aed7155f1c0d2ebd3dd6cccfa0a4e4f86d0f8) | Added contribution/citation guidance, report templates, workflow documentation, and checks for registered guides. | 44 local tooling tests. [Collection workflow passed](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/40618882704). |

The linked workflow results belong to those commits. A later green run does not replace an earlier receipt or expand its scientific scope.

[Contributing](../CONTRIBUTING.md) · [Run and verify](VERIFICATION.md) · [Documentation](README.md)
