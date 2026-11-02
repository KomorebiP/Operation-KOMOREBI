# Lean checked on the reader's device

`lean/browser/index.html` runs the actual Lean elaborator and kernel compiled to
WebAssembly in a persistent Web Worker. It needs no reader account or compiler
service. The page fetches static compiler artifacts; proof edits are never sent
to a remote proof checker.

The picker offers 16 prepared workspaces across nine existing reading editions:
Papers II, III, VII, IX, X, XI and XII, Proof Path Theory and Komorebi Space.
The complete retained files are listed in
`tools/lean_workspaces.py`; the picker groups them by reading edition. Recovery
also compiles its actual local `ProofPath.Compression` import. These are experiments in the browser
environment, not replays of every retained Lake environment or the collection's
2,249 displayed files. Original source bytes, receipts and verification labels
are unchanged. Unsupported imports fail.

“Open another retained Lean file” browses the full reading collection, using the
existing portable source bundle. Its import planner resolves local dependencies
inside the same reading edition and orders them before the selected file. The
available-import filter is a preflight result, not a proof verification. A source
can still fail because of APIs, missing tactics, stack limits or other differences
from its retained project. Known prepared examples remain the default choices.

The bundle is downloaded only when another source is opened. The browser checks
its size and SHA-256, reads its ZIP directory without filesystem extraction, and
checks every requested source against the individual receipt-bound hash and size.
Dependencies cannot cross reading-edition ownership. Original downloads use the
exact extracted bytes, including any BOM or CRLF; only the editor normalizes text.
`catalog.json` records each source route, input identity and compatibility source.

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

`prepare_lean_wasm.py` prepares small manifests over compiler-matched public
packs, following imports in the exact Mathlib source revision. Std/Lean/Batteries
artifacts are compared byte for byte with the per-file tree; matching packed
entries are shared, with any remaining files supplied individually. Each
workspace has its own Mathlib import closure, so a small workspace does not
load modules needed only by another. An edited import can expand to the complete
set of compiler-matched modules already present in the pinned upstream packs.
Exploratory workspaces use that set directly; it remains a subset of Mathlib.
The source archive is read in one sequential
pass and its import parsing is shared across closures. The site stores about
9 MB of metadata. Large binaries remain at immutable URLs in the
pinned upstream public GitHub repository. No additional hosting account is used.
SOURCE.json records every remote URL, size and SHA-256, plus local metadata and
input identities. The final site checker verifies these records and enforces
the 1 GiB Pages publication limit.

The service worker serves the compiler's virtual same-origin asset paths by
fetching the pinned public GitHub URLs with CORS and credentials omitted. It
verifies bytes before returning or caching them under checksum-based keys.
Shared packs are downloaded once across library layers. Quota failures allow
checking to continue without persistent caching.
Its cache contains compiler artifacts, not proof edits. Readers can clear it on
the page. The worker is started only after pressing Run.

## Checks and failure states

The adapter holds Emscripten's runtime alive between runs. Without this, idle
asynchronous tactic work caused an exit after apparently successful checking.
An exit, abort, missing artifact, timeout, stopped worker or failed syntax probe
cannot produce a successful result. The Stop control terminates checking and
startup. The initial artifact requires substantial desktop memory and downloads;
mobile support and Firefox/Safari compatibility are not established.
The retained Special Functions `BrowserCoreLocal.lean` was also tried, but hit
`Maximum call stack size exceeded` in this runtime. It is excluded from the
prepared picker; it can be opened experimentally. Its library-only import check
passes, while its declarations still fail. Changing interpreter preference,
deferring compilation and lowering Lean's recursion option did not remove it.

The fork loses some parser diagnostics. The page therefore always runs Lean's
parser in a separate elaboration, against the same import environment. A
completion marker is required; errors in this check are retained, including
errors unrelated to the marker. Module-format `public import` headers are
carried into this separate check as ordinary imports, preserving the imported
notation without changing the retained proof. An absent marker or failed probe fails checking.
This is also why the Lean library is needed even for a small Std proof.
Source controls that the probe cannot preserve are rejected before compilation.
This includes Unicode line and paragraph separators. The retained dependency's
parser coordinates are kept separate from generated export-wrapper and
syntax-guard coordinates, so diagnostics identify the right source line.
Long guard inputs are assembled from bounded Unicode string chunks, with bounded
join nesting, before parsing the complete source. Export wrappers also supply the
original dependency to this syntax check rather than checking only the wrapper.

Workspace dependencies are checked first. A generated wrapper imports Lean,
names the module, opens a public section for exported-only WASM artifacts, and
writes its checked environment to the compiler's temporary `/lib/lean` tree.
The public section is marked `@[expose]` to preserve transparent definition
bodies for dependent proofs.
The dependent source imports that actual module. The main file is checked with
its retained proof text. When dependency source strings are exactly unchanged,
the same worker reuses their checked modules and checks the edited final file.
Any dependency edit starts a fresh worker, reusing cached downloads. Rewriting
modules in a live imported environment caused a stall during the edit test.
Cached dependency warnings remain warnings, and the result explicitly labels
reused checks. Stop and runtime failures discard this cache. Single-file
workspaces retain their warm compiler. Warnings remain visible;
`sorry` is not a clean result. A clean check is not an axiom audit.

Recovery also needs the newer name `dite_eq_left`, which this runtime lacks.
Its workspace explicitly includes a visible, downloadable compatibility lemma
proved from Lean 4.33's `dif_pos`. The lemma is checked in the same run, is
recorded separately from retained source, and introduces no assumption. The
editor and original download keep the retained proof text. Diagnostics are
mapped back to the original lines; wrapper errors are labelled as generated.

Exploratory sources that use this newer name receive a separate generated
`KomorebiBrowser.Compatibility` module with the same checked lemma. Generated
imports make it available without changing the retained proof body. Sources
importing `Mathlib.Tactic` receive another generated module containing only imports
of the available tactic facade modules. It adds no declarations or assumptions,
and is not the complete upstream umbrella. Both generated sources are visible
in the file picker and downloadable. Missing tactics and other APIs still fail.

Unit tests cover source identity, runtime tampering, pack roundtrips, source
routing, module wrappers and result states. Browser validation must also check
the original workspaces, a valid edit, a false proof, malformed syntax, `sorry`,
dependency changes, Stop/restart, the setup reload, and a narrow viewport.

## Extending coverage

Add only receipt-owned sources from existing reading editions to `WORKSPACES`
in `lean_workspaces.py`. List local modules in dependency order. Runtime
preparation derives Mathlib seeds and a separate manifest for each workspace
from those exact sources; the page build rejects missing imports or manifests.
Run the original source and an intentionally false edit in the actual browser
before making an addition available. Missing artifacts in the upstream
closure require a compiler-matched artifact build; a native `.olean` from an
unrelated Lean version is not sufficient. Keep the compiler/download identities
and the browser cache version coordinated when replacing the runtime.
