PAPER I — CURRENT FORMAL DEVELOPMENT
Komorebi P. | 15 October 2026

current/PaperIRelease.lean imports the complete current development, including
the original foundation, Blocks 03–08, and the release additions. The frozen
module order and source hashes are in current/release_modules.json. Four
positive boundary-consumer modules are included in this closure; tests/
ReleaseBoundary.lean adds the retained 25-assertion predecessor suite.

coverage/COVERAGE_108.json is the exact current manuscript correspondence.
Its 69 proof-level records are distinct publication records, not a count of
independent mathematical discoveries. Definitions, three classical inputs,
scope boundaries, and documentary records are classified separately.
Semantic review matches the printed claims to formal types. Lean checks the
formal types and proof terms; it does not parse or certify the English prose.

REPRODUCE THE FORMAL CHECK

Use the pinned Komorebi_Portable_Lean_4.34.0-rc2 runtime with its original
workspace and upstream dependencies. runtime_bindings.json records the
precise Lean binary, runtime-file hashes, and nine Git dependency revisions.
The small runtime_specification/ directory preserves the exact launcher,
workspace configuration and compatibility-adapter source from that kit.
Lean commit: 6a10ac8c22beadecabdbb0919c2b50214762f91d
Mathlib commit: aeb72f1e9981b6d35b426b16dca7759be3e7ba06

From the release root, run:

  bash formal/verify.sh /absolute/path/to/pinned-runtime /absolute/path/to/new-output

The output directory must not exist. The default rebuilds every frozen
project source, with warnings fatal and implicit-variable guards enabled.
It then audits every source-owned declaration, checks the axiom closure,
rejects twelve deliberate invalid-proof/audit controls, and checks the
entire logical closure starting from upstream imports only. Project objects
shipped as evidence are not used as build inputs.

One generated theorem is also present upstream with exactly identical name,
type, universe parameters, all-list and proof body. Its body is checked by the
kernel under a fresh audit name; the other 3,499 logical declarations are
replayed normally. The union of their original names must match all 3,500
audited logical names exactly. A corrupted-body control checks the fresh-name
verification path. The 13 runtime-only helpers are separately inventoried.

The runtime and multi-gigabyte upstream cache are external prerequisites.
All project Lean modules are included in current/.
The verifier uses Lean's official kernel, not an independent implementation;
runtime files and dependency revisions are checked, while the pinned upstream
cache is reused rather than rebuilt here.
Generated partial runtime helpers are inventoried separately from logical
declarations and are excluded from proof replay.

EVIDENCE

evidence/RELEASE_VERIFICATION.json is the current acceptance summary.
evidence/whole_closure/ contains the fresh compiler and replay logs, exact
source snapshots, source/object hashes, declaration inventories, controls,
and verifier input snapshots. evidence/semantic/ contains the five semantic
review reports. evidence/development/ preserves intermediate author and
reviewer checks with their original scopes and paths; these are provenance,
not substitute final acceptance records.

The source_compilation component shares its 116 byte-identical object files
with whole_closure. Its original receipt is unchanged. See
evidence/source_compilation/OBJECT_LOCATIONS.json and README.txt for the exact
locations and a hash-checking helper that restores the original layout for
optional --base-fresh reuse. Default fresh verification needs no restoration.

The full accepted Block08 archive is retained under source/predecessor/
at the release root. PREDECESSOR.json records its identity. Historical
coverage counts there describe that earlier checkpoint only.

Executable Python examples and their retained lock file are in code/python/
at the release root. Exact manuscript visual checks are in
editable/traditional/visual_checks/. Their recorded limits and run receipts
are under verification/python/. They are bounded computational evidence,
not a universal proof or formal verification of the Python implementation.
