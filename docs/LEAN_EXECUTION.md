# Running the retained Lean sources

The website's [Run with dependencies](https://KomorebiP.github.io/Operation-KOMOREBI/lean/run.html)
page selects every retained Lean file displayed in Inspect Lean. Its generated
catalogue gives the current file and reading-edition counts, environment modes,
and setup status. These counts describe source availability, not accepted proofs.
The native runner preserves source
bytes, builds local imports and records compiler diagnostics. It does not
declare that every retained file is a valid proof. Negative controls,
unfinished proofs, historical code and axiom audits remain distinct inputs.

## Run a selected file

Download `downloads/komorebi-lean-runner.zip` from the site and unzip it.
Install Python 3.11+, Git and [Elan](https://lean-lang.org/install/). In the
bundle folder, use the exact command shown by the selected website file:

```text
python run_lean.py --list
python run_lean.py --source "REPOSITORY_PATH_FROM_THE_LIST" --output ../a-new-run
```

First runs obtain the pinned Lean toolchain and Mathlib cache. The runner uses
`lake setup-file` to build dependencies, then `lake lean FILE -- --json` to
check the selected source using Lake's environment. It checks input hashes
before and after execution and stops if a staged source or configuration changes.
Existing output folders are never silently reused or cleared.

`RUN_INPUTS.json` binds the revision, selected source, staging mode, compiler
pin, target and each copied or generated input hash. `RESULT.json` and
per-step stdout/stderr logs distinguish setup failures, timeouts, rejected
source, warnings and a clean compiler exit. A successful exit does not audit
axioms, exclude every unsafe metaprogram, or establish whole-paper coverage.
The runner returns a nonzero status for warnings, including `sorry` warnings.
The collection's recorded verification labels are not edited by a run.

The manual **Run a selected Lean source** GitHub workflow accepts any exact
selected repository path. It runs on a fresh Ubuntu job without write
permissions or persisted checkout credentials and retains the inputs, result
and logs for 30 days. It needs repository workflow access. Public readers can
run the same bundle locally. Pull requests that change the runner exercise an
original project with custom imports, a reconstructed cross-module proof,
a false-statement control and an unfinished-proof control with native Lean.

## Two kinds of environment

For files with a **retained project**, the original Lake project provides the package
configuration, `lean-toolchain` and `lake-manifest.json`. Their source and
configuration inputs are copied into a new workspace. Compiled objects,
dependency caches, historical result logs and binary publications are omitted.
The original imported package stays untouched.

Other files use a **reconstructed workspace**. Local module imports
are collected from the retained sources of the same work. Resolution prefers
the closest source edition; distinct equally close candidates stop preparation.
Identical leaf modules with only pinned external imports may share one copy.
Nested comments, strings, `public import` and `import all` are accounted for
while routing inputs. Lean itself remains the parser and checker.

This overlay uses Lean `leanprover/lean4:v4.34.0-rc2` and Mathlib commit
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, with the transitive package lock
retained in Paper V's setup. Module files keep their exact bytes. Generated
Lake settings, staging paths and the selected entry filename are recorded
separately. This is a new experiment in a fixed environment, not a recovered
original lockfile or evidence that every source is compatible with it.

`CATALOG.json` records every input's checksum and Git blob, including retained
license records. The build checks these against import receipts and its Git
tree. The page records the downloadable bundle's SHA-256. The site build
constructs and checks the bundle; it does not run Lean automatically.

## Path to interactive checking inside the site

GitHub Pages serves the reader and static source bundle. A dedicated native
Lean backend is the path to editing arbitrary custom-module proofs directly
in that page. The existing public Mathlib editor cannot register these custom
project configurations for us. The browser Wasm pilot is also not a replacement
for the collection's native toolchains, caches, native plugins and project setup.

The runner can export a ready project for the upstream
[lean4web server](https://github.com/leanprover-community/lean4web/blob/main/doc/Projects.md):

```text
python run_lean.py --source "REPOSITORY_PATH_FROM_THE_LIST" --output ../web-export --prepare-only --leanweb-project KomorebiExample
```

Deploy `web-export/project/` as `Projects/KomorebiExample/` on that server,
retaining the bundle's licenses and input records. The generated
`leanweb-config.json` lists the unchanged source as an example. Its build
script fetches the pinned cache and builds imports, leaving the editor to
check the selected source. The named entry file matches the project folder,
as required for the editor's package options. In a multi-project server,
retain one explicitly selected default project.

Use the upstream production isolation with Bubblewrap on Linux. Keep checked
project sources read-only, give each editing session a separate bounded
workspace, retain compiler time/memory limits, and provide no credentials to
Lean processes. This is necessary before exposing arbitrary edited Lean code
to public visitors: Lean metaprograms and `#eval` can execute native IO.
Do not turn off Bubblewrap to work around a deployment failure.

After a backend is deployed, the `.io` page can embed its editor using
`#project=KomorebiExample&url=PUBLIC_ORIGINAL_SOURCE_URL`, following the
[upstream URL interface](https://github.com/leanprover-community/lean4web/blob/main/doc/Usage.md).
This preserves the static reader while the server supplies the actual pinned
project and dependencies. A hosting destination and operator-controlled
session/resource policy are still needed; the bundle and workflow do not
silently provision a public server or pretend that one already exists.
