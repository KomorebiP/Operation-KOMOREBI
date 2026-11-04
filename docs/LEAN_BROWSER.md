# Lean checked on the reader's device

`lean/browser/index.html` runs the actual Lean elaborator and kernel compiled to
WebAssembly in a persistent Web Worker. It needs no reader account or compiler
service. The page fetches static compiler artifacts; proof edits are never sent
to a remote proof checker.

The picker offers 17 prepared workspaces across ten existing reading editions:
Papers II, III, VII, IX, X, XI and XII, Proof Path Theory, Komorebi Space and
Special Functions.
The complete retained files are listed in
`tools/lean_workspaces.py`; the picker groups them by reading edition. Recovery
also compiles its actual local `ProofPath.Compression` import. These are experiments in the browser
environment, not replays of every retained Lake environment or the full reading
collection. Original source bytes, receipts and verification labels
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

Some missing Mathlib modules can be compiled from their original source on the
reader's device. A bounded allowlist is extracted from the checksum-verified
Mathlib source archive at the compiler-matched revision. Each source retains its
copyright header, exact bytes, upstream link, revision, size and SHA-256. The
catalog lists these separately from the receipt-bound paper sources and orders
their dependencies first. Library sources and retained sources share a single
import order: each library is compiled before the first file that imports it,
after earlier independent project dependencies. This avoids an observed runtime
trap when the positivity sources were loaded before the unrelated quantum
arithmetic and Fourier modules. The order is recomputed from the original import
graph during site verification; duplicate, missing and invalid steps are rejected.
The browser checks their bytes and compiles each
library module with the same syntax check and module-export wrapper used for
local dependencies. A failed library check stops the workspace. Library source
edits invalidate the worker's dependency cache just like paper dependency edits.
The file picker labels these as library sources; they are not generated stubs or
additions to the Mathlib.Tactic compatibility umbrella.
The source allowlist is `Mathlib.Tactic.Ext`, `Mathlib.Util.AssertNoSorry`,
`Mathlib.Tactic.Positivity.Finset` and `Mathlib.Tactic.Positivity`. The latter two
provide the original finset positivity extensions and their small import
umbrella. Routes that need Finset automatically enable experimental
source-defined syntax checking for the whole workspace. The checkbox is checked
and locked for that route, and the route notes explain why. Selecting a different
workspace restores the reader's chosen mode. This requirement is recorded with
the pinned library source; unknown checking modes are rejected. These routes
start a fresh compiler on every run and reject background tasks. Other candidates
remain unavailable until their actual browser compilation succeeds. The standard
syntax probe can reject same-file namespace or notation changes, and the runtime
still has private declaration and interpreter limits.

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
pass and its import parsing is shared across closures. The site stores compact
manifests and source metadata. Most large binaries remain at immutable URLs in
the pinned upstream public GitHub repository. A bounded Paper III pilot also
serves about 24.5 MiB of smaller compiled module packs from a separate asset-only
branch in this repository. The source pins immutable asset commit
`d309a96db5a7d17cdb8aa579da92fc5c9316d53a`; this branch must not be merged into
main. Pack binaries and provenance JSON stay outside the Pages artifact.
Proof Path's Compression and Recovery workspaces reuse those same 298 packs
and add 62 qualified module triplets from immutable asset commit
`d91c4cd35509edc4e57bd19ee427bf4a36660ce2`. Both use one shared library manifest;
their source files, compatibility helper and checking order remain separate.
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

The first-load notice counts unique compiler/library asset bodies for the
selected workspace, including its manifests and download record. Shared paths
are counted once, and all three standard-library roots are budgeted. Experimental
syntax uses the broader library plan. These are conservative plans for the
original imports; edited imports can load more. The notice updates without
starting a compiler.

## Checks and failure states

The adapter holds Emscripten's runtime alive between runs. Without this, idle
asynchronous tactic work caused an exit after apparently successful checking.
An exit, abort, missing artifact, timeout, stopped worker or failed syntax probe
cannot produce a successful result. The Stop control terminates checking and
startup. The initial artifact requires substantial desktop memory and downloads;
mobile support and Firefox/Safari compatibility are not established.
An incomplete library installation reports its download or unpacking error
immediately instead of continuing with a partially installed library tree.
The pinned binary routes exception-aware indirect calls through JavaScript,
which exhausted the browser stack on the retained Special Functions
`BrowserCoreLocal.lean`. The adapter now moves those calls into a small Wasm
module, sharing the compiler's original function table. All original function
indices, bodies and table entries remain unchanged. The original start function
runs after the native stack helpers are bound, before Emscripten initialization.
The unchanged Special Functions file completed with no diagnostics in the
browser after this change. Larger sources can still exceed runtime limits.

The transformation happens in memory after the original pinned downloads pass
integrity checks. It validates all 39 original invoke-wrapper bodies and their
signatures, including numeric exception handling and return coercions. The
script and Wasm change as one pair; unsupported browser features or an
unrecognized artifact keep the complete original pair and report the fallback.
JavaScript and native exceptions restore the linear-memory stack before
propagation. Direct Wasm traps are fatal: the failed check discards its worker.
The original downloaded bytes and their checksum cache are unchanged.

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

Workspace dependencies are checked before their importers. A generated wrapper imports Lean,
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
Runtime failures identify the file being checked and retain earlier completed
results, without giving the interrupted workspace a successful result.

Drafts saved across the browser-isolation reload include module, path and source
role identities. They are matched by identity if the checking order changes.
An older or mismatched draft is kept in session storage and offered as a download,
without applying its text to different files or automatically running it.

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

## Experimental source-defined syntax

The optional “Support syntax defined in this file” checkbox selects a single
synchronous frontend pass. It parses and elaborates commands in order, using
the evolving namespace, options, open declarations and parser environment.
This supports commands and scoped notation declared earlier in the same file.
The default checker remains the existing compiler plus separate syntax probe.

The experimental transport imports only its fixed Lean implementation. It
parses the original header and imports that exact ordered set of import records
into a separate environment, preserving meta/public/all flags. It does not
give a Std-only source access to the transport's extra Lean imports. The main
module is set before creating fresh command state for a project dependency.
The transport adopts the source's imported and final environments so outer
command callbacks see all newly registered environment extensions. The
compiler's header-environment cache is reset before each source; checked
module files remain in the worker's filesystem for dependent sources.
Parser messages are saved before command elaboration clears them, then genuine
parser and elaboration messages are copied back with their source coordinates.

The browser preloads available libraries and invokes the transport exactly
once per source, with no retry after execution. A fresh random nonce identifies
distinct started and completed messages. A result needs the exact completed
message, successful runtime completion and no errors. The frontend consumes
already completed command snapshots, including all descendants and both reported
and unreported diagnostics. It checks readiness before reading any task, rejects
cancelled or fatal snapshots, and bounds both visits and the pending frontier to
10,000 nodes per command. The checked kernel environment must also be ready with
trust level zero; snapshot diagnostics remain necessary because kernel failures
can retain the previous environment. Tasks are cleared only after these checks.
Small nonce-named transport helpers keep the generated driver within the browser's
elaboration stack limit and stay outside the source's exact import environment.

Unfinished tasks, early terminal commands and active asynchronous scopes are
rejected. Literal `set_option Elab.async true` forms in commands, terms and tactics
are rejected before elaboration, including scoped forms that restore their options
before the next command. Comments, strings and quoted syntax do not trigger this
syntax check. Macro-generated options and arbitrary metaprogram option changes are
not comprehensively observed by that check; task and diagnostic validation still
applies to every executed command. Both checking
paths require actual end of input, so `#exit` cannot leave an unchecked tail.
Internal panic output fails checking even if captured as information or followed
by a completion message.
Original source controls are rejected before any string encoding or wrapping.

Every experimental Run starts a fresh worker and disposes it on completion,
failure or Stop. Imported environments use leaked compacted regions in this
fork, so reusing these environments across repeated runs exhausted memory in
testing. Large dependency chains can still exhaust memory within one run.
The page owns the wrapper, Wasm and glue Blob URLs and revokes them when the
runtime closes. Idle disposal asks the worker to terminate its pthread pool,
with a 100 ms hard-termination fallback. Stop during startup or an active request
terminates immediately; fatal and incomplete checks also force termination.
`compiler.dispose()` returns `compiler.closed`, which resolves after termination
was requested and the owned URLs were revoked. This does not certify immediate
physical reclamation of every shared-memory mapping. The page waits for the prior
compiler's closure before creating its replacement, including after Stop.
Exhausted memory is reported separately from unavailable cross-origin isolation,
without an automatic retry.
This mode retains the fork's exported-only import and synchronous command
semantics; it does not establish equivalence with every native project or
whole-file linter. The private-theorem visibility issue is separate.

Manual browser controls are saved in
[`tools/fixtures/lean_frontend_tasks.json`](../tools/fixtures/lean_frontend_tasks.json).
Copy one case's `source` into a single-file prepared workspace with experimental
checking enabled and run it with a fresh compiler. Check both `expected_outcome`
and the literal `expected_marker` in Lean's response. The corpus includes hidden
reported errors, descendant warnings, unfinished/cancelled/fatal tasks, bounds,
scoped options, import isolation and a filesystem counter that detects replay.
These are browser fixtures, not a claim that the JavaScript unit suite executes Lean.

## Extending coverage

### Selected checks and bounded loading

The page offers **Check selected file** alongside the complete workspace check.
It plans the selected file's transitive local imports from the current edited
sources, checks each ancestor once in deterministic dependency order, and checks
the selected file with its original target role. Unrelated files are omitted.
The response identifies the target and how many workspace files were included;
a successful selected check does not claim that the whole workspace passed.
The whole-workspace action remains available.

Selected planning accepts ordinary line-based import headers, including supported
module markers and import visibility flags. Missing project imports, cycles,
duplicate modules and ambiguous or unsupported headers fail before compilation.
Quoted or multiline import forms and some custom command layouts may need an
explicit whole-workspace check. Generated compatibility dependencies are included.
The intended check scope survives the isolation setup reload. A target-role or
dependency-source change retires the old compiler; standard checks can reuse
unchanged checked dependency results and their warnings in the same worker.
Recovery's inline version-compatibility lemma accompanies its final file only.
Experimental checking still starts fresh and retains all existing completion guards.

Library loading overlaps up to two encoded pack downloads. Each prefetchable pack
is at most 8 MiB, so the worker retains at most 16 MiB of those encoded bodies,
including completed lookahead. Unknown or larger sizes use an exclusive serial
fallback. SHA verification, decompression and filesystem installation stay serial,
in manifest order. A download or installation failure aborts and drains pending
prefetch work. Stop still terminates the active compiler immediately. This budget
does not include decoded libraries, the Wasm heap, or browser/network internals;
service-worker upstream requests may finish caching after a client is stopped.

### Route to broader browser support

1. **Smaller verified library assets.** Paper III's Coordinate naturality workspace
   uses a delivery pilot of 298 complete module triplets (894 unchanged files).
   Its Mathlib-layer packs contain about 24.5 MiB instead of 110.9 MiB in the
   original shared packs. Each new pack is addressed by its compressed SHA-256.
   The independently pinned `manifests/lean-module-pilot.json` binds original
   compressed inputs, original member tables and every decoded artifact hash.
   Original-input qualification stages one original pack at a time through
   temporary files and compresses one module at a time. Generated-output checks
   reject altered decoded bytes even after output hashes are recomputed.
   The independently pinned `manifests/lean-module-pilot-delivery.json` freezes
   the already qualified publication bytes, avoiding gzip differences across
   Python/zlib versions. Build and site verification bind every remote URL,
   size, checksum, member table and delivery total to these receipts. The browser
   verifies the frozen compressed hashes before inflation and installation.
   Standard libraries retain their original delivery; experimental frontend mode
   and expanded edited imports can still use the broad original Mathlib layer.
   The reduction describes this layer's asset bodies, not the whole compiler
   download, a proof-speed result or a Wasm-heap reduction. The separate asset
   branch keeps pilot binaries outside Pages; its existing size limit still applies.
   Paired browser controls with the original proof requested about 292.1 MiB
   versus 229.7 MiB of unique engine response bodies, including download records
   and manifests: about 21% less data. The number of unique responses rose from
   401 to 685. These counts describe response bodies, not HTTP overhead, network
   cache behavior or a controlled latency benchmark.
   Wider rollout needs request-overhead and shared-cache measurements across
   workspaces. HTTP byte ranges cannot directly select members of the original
   gzip containers because manifest offsets describe the uncompressed bytes.
   The Proof Path extension covers 360 complete triplets (1,080 unchanged
   artifact files), with 298 reused from Paper III and 62 additions. Its layer
   totals about 29.9 MiB instead of 117.6 MiB in original shared packs. The
   independent `manifests/lean-proof-path-modules.json` binds the original member
   hashes and both import closures; `manifests/lean-proof-path-delivery.json`
   freezes the output pack tables and encoded hashes. Preparation rechecks every
   original member without recompressing the frozen extension. Both workspaces
   share `workspaces/proof-path-compression.json`, and the verifier pins that
   alias, each workspace's module set, all new asset records and reuse totals.
   No extension binaries or receipt JSON are copied into Pages.
   Generated JSON uses LF endings and standard-root inventories use POSIX-path
   ordering, so Windows and Linux produce the same metadata bodies.
   Optional transfer bundles address the request overhead without changing those
   individual artifact identities. The independently pinned
   `manifests/lean-transfer-bundles.json` groups 708 existing encoded module packs
   and Batteries files into 40 concatenated bodies totaling 37,250,418 bytes.
   No member is recompressed. Each body is at most 1 MiB (the largest is
   1,045,291 bytes). Immutable assets live on a separate asset branch; build and
   site verification reject transfer binaries copied into Pages. SOURCE includes
   the pinned group projection and remote records; its metadata grows by 69,242
   bytes for this delivery revision.

   The service worker serves existing checked individual cache keys first. On a
   miss it considers a bundle only when at least two members and half of its
   encoded bytes are missing. Otherwise it fetches the missing file individually.
   Concurrent requests share one group task, with at most two active downloads
   and eight pending groups; excess work uses ordinary individual delivery.
   A group has an exact bounded length, an outer SHA-256, and a separate hash
   check for every member before any member enters the cache. A failed optional
   transfer falls back to the original individually checked URL. Legacy SOURCE
   records remain usable. Quota failures retain at most two encoded groups in
   temporary service-worker memory, separate from the compiler. These limits do
   not bound the Wasm heap or browser/network memory. Stop terminates compilation;
   already active service-worker transfers can finish populating artifact caches.

   A controlled cold-cache browser pair checked the original Proof Path Compression
   source successfully with 747 virtual engine bodies in both cases. Upstream
   asset requests fell from 741 to 73 (40 bundles plus 33 other bodies), while
   upstream encoded payload stayed exactly 243,846,832 bytes. Switching to Recovery
   then checked both original workspace files without another upstream asset fetch.
   The pair used identical verified local bodies and a fixed 50 ms response delay;
   it does not establish a public-network speed or memory improvement. Virtual
   response counts include local metadata and differ from upstream requests.

2. **Checked module artifacts before parallel compilers.** Qualify complete
   export/import round trips in a fresh compiler, including corrupted parts,
   stale generations, edits, warnings, initializers and Stop. The fixed Proof Path
   qualification below exercises a real retained-source dependency and consumer. The current
   heavy checkpoint experiment exported artifacts but did not establish successful
   fresh-worker import. Cache authorization must come from successful checks,
   not just matching byte hashes. Bind source, module role, ordered imports,
   transitive dependency receipts, compiler/library versions and guard policy;
   invalidate edited nodes and every dependent module.
3. **Memory-budgeted independent branches.** Keep one heavy compiler active by
   default. Only independent modules in the dependency graph are candidates for
   separate workers, after artifact interchange and aggregate memory limits are
   validated. The Quantum/Finite/Semantic chain is inherently dependent. Fresh
   imports can repeat initialization effects and reset mutable state; arbitrary
   command splitting does not preserve parser, namespace and environment state.
4. **Compiler compatibility and larger individual modules.** Add missing
   compiler-matched artifacts and qualify asynchronous elaboration separately,
   preserving false-proof, kernel-error, cancellation and completion controls.
   Scheduling cannot make a single module fit if its own environment exceeds the
   browser runtime's memory capacity. A compatible larger-memory compiler build
   is a separate investigation.

Pinned source archives and upstream runtime inputs are also candidates for CI
caching, with independently reviewed receipt checks on every cache hit. A cache's
own checksum manifest is not sufficient provenance. This can shorten publishing
without weakening source or runtime validation.

### Reproducing the module-transfer qualification

`tools/lean_checkpoint_probe.py` creates a separate developer probe from a verified
prepared runtime and the current production adapter. It preserves the public
loader. The probe accepts only the original `ProofPath.Compression` wrapper and
original `ProofPath.Recovery` with the existing, separately recorded compatibility
lemma, plus its explicitly false consumer control. This fixed-source policy uses
the independently qualified Proof Path import closure before source execution;
it does not add a general selective frontend or cache API.

From a prepared checkout, use a new output directory:

```sh
python -B tools/lean_checkpoint_probe.py --runtime .reader-build/lean-wasm --output .reader-build/checkpoint-trial --serve --port 8000
```

Open `http://127.0.0.1:8000/lean/browser/checkpoint.html` and press **Run transfer
controls**. The local server supplies the isolation headers needed by the pinned
pthread compiler. The generated graph records every adapter file and the exact
runtime, frontend, wrapper, original sources, library manifests and native runtime
pair. Node must be available; `--node /path/to/node` selects an explicit executable.
The output directory is never overwritten and cannot be inside the runtime.

The browser qualification exported five complete Compression parts totaling
19,144 bytes, closed the producer, and checked Recovery successfully in a distinct
fresh compiler. Its false equality was rejected. Corrupt and missing-part controls
ran zero consumer compiles. The source producer ran once; these observations do
not establish a speedup, lower peak memory or initialization-state continuity.
The [recorded browser result](../verification/browser-lean/proof-path-checkpoint-2026-11-04.json)
binds this observation to its generated graph and source inputs.

Export authorization requires a final clean synchronous frontend result, including
its completion marker; warnings cannot mint a receipt. A private in-memory issuance
seal binds the exact five parts to one originating run. Recomputed public hashes
cannot authorize a replacement. Installation clones inputs before awaiting hashes,
consumes its seal once, checks source/build/session bindings and limits before
writing, and runs with an exclusive worker phase. Any stage or rename failure
invalidates the receiver, including a partially committed filesystem. All five
parts are required, with 16 MiB per-part and 64 MiB total limits checked before
export reads. Stop aborts the run's authorization and cannot schedule a consumer.
The pause checkbox makes Stop before handoff reproducible; an explicit later Run
starts a fresh producer. Source and import failures never trigger source retries.

For the generated graph, `node tools/test_lean_checkpoint_probe.mjs
.reader-build/checkpoint-trial` tests receipt issuance, tampering, competing
installs, cancellation, owned buffers and injected filesystem failures with mocked
native compilation. These checks do not run Lean; the browser control above is
separate. CI builds and checks this probe but does not publish it into Pages.
Imports in fresh processes can execute initializers again. Persistent artifacts,
arbitrary edited modules, heavier checkpoints and parallel compilers still need
separate qualification.

### Adding a published workspace

Add only receipt-owned sources from existing reading editions to `WORKSPACES`
in `lean_workspaces.py`. List local modules in dependency order. Runtime
preparation derives Mathlib seeds and a separate manifest for each workspace
from those exact sources; the page build rejects missing imports or manifests.
Run the original source and an intentionally false edit in the actual browser
before making an addition available. Missing artifacts in the upstream
closure require compiler-matched source compilation or an artifact build; a native `.olean` from an
unrelated Lean version is not sufficient. Keep the compiler/download identities
and the browser cache version coordinated when replacing the runtime.
