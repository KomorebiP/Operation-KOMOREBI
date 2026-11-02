# Lean checked on the reader's device

`lean/browser/index.html` runs the actual Lean elaborator and kernel compiled to
WebAssembly in a persistent Web Worker. It needs no reader account or compiler
service. The page fetches static compiler artifacts; proof edits are never sent
to a remote proof checker.

The initial prepared workspaces are Paper X's complete `Residual.lean`, Proof
Path Theory's `Compression.lean` with Mathlib, and `Recovery.lean` with its actual
local `ProofPath.Compression` import. These are experiments in the browser
environment, not replays of every retained Lake environment or the collection's
2,249 displayed files. Original source bytes, receipts and verification labels
are unchanged. Unsupported imports fail.

## Environment and static hosting

The compiler is cauli's Lean fork at
`62b6a2291302d4bbeace37642a066b7510d0145c` (Lean 4.33.0); Mathlib artifacts are
from `de3a9cf33016bbb6d15880d7680643f7ca2d25ba`. The adapter and input assets
are pinned to live-codes/browser-lean
`a8aed095534e67061e2626b94e8e69193099091d`.

The available binary uses pthreads and shared memory. An opt-in service worker
adds COOP/COEP to the browser workspace's own responses, following
[coi-serviceworker](https://github.com/gzuidhof/coi-serviceworker). Its scope is
only `/lean/browser/`, including under the site's project prefix. GitHub Pages
needs no custom headers. The initial setup reload saves the selected workspace
and drafts to session storage and resumes the requested run. It has a loop guard.
Browsers without the required facilities get a failure message and no successful
result. The page can be tested on an ordinary localhost HTTP server with no
headers. A single-threaded binary could later remove this isolation step.

`prepare_lean_wasm.py` repackages compiler-matched libraries into gzip packs with
explicit offsets and SHA-256 checksums. It follows imports in the exact Mathlib
source revision to retain the prepared examples' Mathlib closure and excludes
duplicated core/Std/Lean/Batteries data. SOURCE.json records input and output
identities. The workflow verifies and copies these assets into the published
site; large binaries are not added to this repository's source tree. The final
site checker enforces the 1 GiB Pages publication limit.

The service worker caches verified compiler downloads under checksum-based
keys. Quota failures allow checking to continue without persistent caching.
Its cache contains compiler artifacts, not proof edits. Readers can clear it on
the page. The worker is started only after pressing Run.

## Checks and failure states

The adapter holds Emscripten's runtime alive between runs. Without this, idle
asynchronous tactic work caused an exit after apparently successful checking.
An exit, abort, missing artifact, timeout, stopped worker or failed syntax probe
cannot produce a successful result. The Stop control terminates checking and
startup. The initial artifact requires substantial desktop memory and downloads;
mobile support and Firefox/Safari compatibility are not established.

The fork loses some parser diagnostics. The page therefore always runs Lean's
parser in a separate elaboration, against the same import environment. A
completion marker is required; errors in this check are retained, including
errors unrelated to the marker. An absent marker or failed probe fails checking.
This is also why the Lean library is needed even for a small Std proof.

Workspace dependencies are checked first. A generated wrapper imports Lean,
names the module, opens a public section for exported-only WASM artifacts, and
writes its checked environment to the compiler's temporary `/lib/lean` tree.
The public section is marked `@[expose]` to preserve transparent definition
bodies for dependent proofs.
The dependent source imports that actual module. The main file is checked with
its retained proof text. The workspace environment cache is reset before each
run to avoid reusing stale dependency environments. Warnings remain visible;
`sorry` is not a clean result. A clean check is not an axiom audit.

Recovery also needs the newer name `dite_eq_left`, which this runtime lacks.
Its workspace explicitly includes a visible, downloadable compatibility lemma
proved from Lean 4.33's `dif_pos`. The lemma is checked in the same run, is
recorded separately from retained source, and introduces no assumption. The
editor and original download keep the retained proof text. Diagnostics are
mapped back to the original lines; wrapper errors are labelled as generated.

Unit tests cover source identity, runtime tampering, pack roundtrips, source
routing, module wrappers and result states. Browser validation must also check
the original workspaces, a valid edit, a false proof, malformed syntax, `sorry`,
dependency changes, Stop/restart, the setup reload, and a narrow viewport.

## Extending coverage

Add only receipt-owned sources from existing reading editions to `WORKSPACES`
in `lean_browser.py`. List local modules in dependency order and add necessary
Mathlib seeds to `prepare_lean_wasm.py`. Missing artifacts in the upstream
closure require a compiler-matched artifact build; a native `.olean` from an
unrelated Lean version is not sufficient. Keep the compiler/download identities
and the browser cache version coordinated when replacing the runtime.
