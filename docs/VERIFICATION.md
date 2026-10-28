# Run and verify the collection

**Komorebi P. · Work in progress · 27 October 2026**

Operation-KOMOREBI contains separate manuscripts, formal projects, packages, and experiments. Select a component before installing dependencies or attempting a build. All executable software is **beta / work in progress**; each result applies to its recorded revision, environment, and tested scope.

## Obtain a checkout

You can read the collection on GitHub without installing anything. To run the collection's Git-based checks, use Git and Python. The collection workflow uses Python 3.13 on Ubuntu 24.04. The small example below requires Python 3.10 or later and the standard library.

From a directory where you want a new copy:

```text
git -c core.longpaths=true clone https://github.com/KomorebiP/Operation-KOMOREBI.git
cd Operation-KOMOREBI
git rev-parse HEAD
python --version
```

This is a large collection, so checkout can take time. The long-path setting helps Git for Windows handle the nested source directories. Use a short parent path if Windows tools encounter path-length errors. In shells where Python is named `python3`, substitute that command. Confirm that the interpreter is the version you intend to test.

Use a normal Git clone with history for the status checks: they read both the current committed tree and the assessed source revision. A downloaded ZIP has no Git history, and a shallow clone can omit the required revision. From a shallow clone, `git fetch --unshallow` restores the history. Record the output of `git rev-parse HEAD` with any result.

Checkout contents and Git history are separate requirements. `check_repository.py` needs the entry-point files, imported contribution paths, and entire preserved preview on disk. A sparse checkout can omit them even when the commit exists. The checker reports missing prerequisites as JSON with a nonzero exit status; a preview marked `NOT_RUN` is an incomplete check. Use a complete checkout for the full collection workflow. The source-receipt checker reads committed Git objects and can operate with sparse checkout contents.

## Run the small example

From the collection root:

```text
python -B formal/research-preview-1/demo.py
```

Expected output is JSON containing `"status": "PASS"` and `"scalar_coefficient_comparisons": 96`. There are three mask cases, with 32 coefficients per case. The reference implementation uses exact integer and modular arithmetic and compares a finite Cartier machine with a separately computed recurrence. It does not run Lean or the minimal-realization compiler.

For a larger example, the same script accepts `--count 256`, producing 768 scalar comparisons. Its optional `--output PATH` writes a receipt; choose a new path outside retained evidence. The [preview reproduction guide](../formal/research-preview-1/REPRODUCE.md) describes the separate reference audits and proof replay.

## Check the collection

Run these commands from the collection root, with Git on the command path:

```text
python -B tools/check_repository.py
python -B tools/check_source_receipts.py
python -B tools/update_completion_status.py --check
python -B -m unittest discover -s tools -p "test_*.py" -v
```

Each command must finish with exit status zero. Read its scope and diagnostics as well as the status.

| Command | What it checks |
|---|---|
| `check_repository.py` | Required entry points, contribution paths, and the preserved research preview's source/artifact identity. |
| `check_source_receipts.py` | All selected component receipts against the committed Git tree: configuration, counts, aggregate record digests, paths, Git blob identities, and modes. It defaults to `HEAD`; it does not certify arbitrary working-tree edits. |
| `update_completion_status.py --check` | Status/evidence correspondence, maintained relative links, and all generated reader and status pages. It validates recorded evidence without rerunning its original proofs or experiments. |
| Tools regression suite | Collection import, receipt, and navigation tooling behavior. |

Source identity does not establish mathematical correctness. These commands do not perform a new SHA-256 read of every source blob or replay every Lean project. For a package's own tests, use its instructions and supported dependencies.

The [workflow guide](WORKFLOWS.md) maps the eight workflows, their triggers, and their publication effects. The [collection workflow](../.github/workflows/artifact-checks.yml) also runs the preview's receipt/upload-guard tests and proof-diagnostic classifier self-test. To reproduce those steps, change to `formal/research-preview-1/` and run:

```text
python -B -m unittest discover -s tests -p "test_*.py" -v
python -B tools/replay_lean.py --self-test
```

The classifier self-test checks diagnostic handling; it does not invoke the Lean compiler. The workflow's success applies to these checks on its displayed commit. [View workflow runs](https://github.com/KomorebiP/Operation-KOMOREBI/actions/workflows/artifact-checks.yml).

## Reproduce a component result

1. Locate the exact edition in the [component index](COMPONENT_INDEX.md) and its evidence in the [status catalogue](STATUS_CATALOG.md).
2. Read that component's requirements, input limits, claim map, and reproduction instructions. Use its pinned toolchain and dependency revisions where specified.
3. Work in a separate copy or fresh output directory. Record the source commit, commands, input data, dependency versions, platform, exit statuses, and output.
4. Compare the observed results with the stated acceptance criteria, including negative controls. Keep failures and environmental blockers in the record.

For formal proofs, follow the [formalization guide](../formal/README.md) and the selected project's instructions. The preview's pinned Lean reproduction path is in [REPRODUCE.md](../formal/research-preview-1/REPRODUCE.md). Package tests, compilation evidence, and correspondence between prose and formal statements need their own checks.

For software, see the [software guide](LIBRARIES.md). The [Constructive Repair guide](components/CONSTRUCTIVE_REPAIR.md) documents partial Windows qualification, the rebuilt wheel's source correspondence, and the two unresolved symlink-fixture checks. Independent library qualification is tracked in the corresponding repository.

Preserved component files can contain historical descriptions such as “unpublished,” “private-only,” or an earlier licensing decision. Those describe their original checkpoint. The maintained [publication status](PUBLICATION_STATUS.md), [collection terms](../LICENSE.md), and component notices explain the current public collection.

## Interpret a failure

| Observation | Next step |
|---|---|
| Assessed Git revision is missing | Confirm this is a Git checkout and obtain its history; a source ZIP cannot supply commit objects. |
| Preview is `NOT_RUN` or entry-point files are missing | Confirm the checkout includes the required files and entire preserved preview directory. Inspect the recorded reason for a launch failure. A partial checkout is not a successful artifact check. |
| Preview output is malformed, reports failure, or exits nonzero | Read `preview`, `preview_exit_status`, and any `preview_stderr`. Both JSON `PASS` and exit status zero are required. |
| A generated page is stale | Review the intended source/template change, regenerate the pages, and inspect the diff before committing. |
| A source hash or evidence binding differs | Identify the changed bytes and edition. Record a corrected revision with new evidence instead of overwriting the old receipt. |
| Temporary directory or symlink setup fails | Use a writable temporary directory or an environment with the required fixture capability, then rerun. The blocked test remains unverified. |
| A negative control fails for an import, timeout, or setup reason | Resolve that prerequisite; only its intended rejection satisfies the control. |

Report a failure with the commit, exact command, platform, relevant dependency versions, and diagnostic output. Remove credentials and unrelated personal paths before sharing logs.

## Maintaining reader pages

The [maintenance guide](MAINTENANCE.md) maps each script to its inputs and file/publication effects and explains how to preserve dated records.

Direct reading and source links are selected in [browse-resources.json](../manifests/browse-resources.json) and rendered by [browse_navigation.py](../tools/browse_navigation.py). The same status command checks their receipt ownership, committed paths, file types, and navigation anchors. Each primary work has a generated page under `docs/works/` connecting its reading files, written proofs, Lean, code, and evidence; the evidence catalogue provides a return link. The browse pages reuse the existing completion, Lean, and confidence labels.

The command's `navigation_links` result counts checked inline relative links, directory links, and fragments in maintained/generated documents. Paths are case-sensitive, encoded file names are decoded, and example code blocks cannot supply navigation targets. Remote URLs and fragments in preserved source documents are counted separately as unchecked. A passing result establishes repository navigation within that scope; it does not certify remote services or make untagged PDFs accessible.

The proof, Lean, and code finders now have per-work anchors and return links to the same work section. The maintained-page check validates both ends. Lean setup documents are validated as text files and shown separately from actual Lean sources; instructions alone do not qualify an entry for the Lean-source finder. Source shortcuts may open a module directory within a larger historical project, so use the accompanying setup guide to locate the build root before running commands.

The top-level README and category/reading guides are generated by [update_source_navigation.py](../tools/update_source_navigation.py). Documentation, record, manifest, verification, and history indexes are generated by [record_navigation.py](../tools/record_navigation.py) from the existing registry and committed history paths. Completion labels, evidence references, and the finalization queue are driven by [project-status.json](../manifests/project-status.json). Edit the appropriate template or record, then run from the collection root:

```text
python -B tools/update_completion_status.py
python -B tools/update_completion_status.py --check
git diff --check
git diff --stat
```

Review the resulting diff before publication. This regenerates all maintained navigation/status outputs and validates the additional documents registered in the status manifest. It does not revise the original scientific source packages. The public authorship statement, distribution notice, component guides, historical snapshots, contribution/citation guides, and GitHub issue/pull-request templates are maintained separately and checked through that registration. Add a new report to the appropriate registry with its evidence bindings; the records index then includes it automatically. Keep the maintenance focus in the status manifest current without changing scientific labels merely to reflect scheduling.

The [finalization queue](FINALIZATION_QUEUE.md) names remaining work and its completion criteria. Update a status only when the corresponding evidence supports it.

## SRIC admission records

The [0.3.3 repair guide](SRIC_REPAIR_2026-10-27.md) identifies the corrected source edition and its 15-test qualification suite. The collection workflow installs NumPy 2.3.5 and runs:

```text
python -B packages/sric-admission-v0.3.3/tests/test_admission_boundaries.py
```

This includes a synthetic CLI round trip and rejection controls; no real checkpoint is downloaded or qualified. The earlier [admission audit](SRIC_ADMISSION_AUDIT_2026-10-27.md) retains seven diagnostic fixture executions and three reproduced gaps in the old pipeline. Its harness is a historical counterexample record, not the repaired runtime's acceptance suite.

[Documentation](README.md) · [Records guide](RECORDS.md) · [Public project statement](PROJECT_STATEMENT.md) · [Collection](../README.md)
