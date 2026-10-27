# PHYS-CENT-51 verification and delivery engineering review

Verdict: **PASS for the inspected engineering design and exact sources below.**
This is a read-only review of the verifier and sealer, not a final acceptance
run and not an independent kernel implementation. No production, gate, runtime,
or packaging source was changed by this reviewer.

## Exact reviewed inputs

| Input | SHA-256 |
|---|---|
| `seal_release.py` | `ed94231b36045f2e614c4078c401600dc6c431a9b47880af27f26fe113f50807` |
| `gate_tools/verify_centered.py` | `2ae5b2e524b3a7527b4a762bc6914296dc06e90ee11056fba6eaaf6c7a1eaa26` |
| Project `CONTROL_MANIFEST.json` | `0d53bad691e3770b8dff0178599fda77d36e717e406f9e3c4567d4caebe73873` |
| Pinned runtime manifest | `3d038009d119676dd1e61146556da63379bccbf2ae89fac6e33f1efa147e8f05` |

## Delivery integrity

The sealer records every regular payload file with relative path, byte size,
and SHA-256. Only the root manifest is excluded from its own inventory. The
verifier compares the complete ordered inventory, so missing files, added files,
renames, size changes, and byte changes are detected. Symlinks, special files,
Python bytecode caches, and duplicate manifest paths are rejected. Empty
directories are deliberately outside the file-set claim.

The sealer refuses an existing output directory, an output inside the release,
or a preexisting root manifest. The archive uses exclusive creation. A failure
preserves its partial output and records failure; it does not silently resume or
replace a prior seal. A new assembly/output is needed for a retry after the
manifest has been written.

ZIP membership must equal the manifest payload plus the manifest itself, with no
duplicate members. CRC verification precedes extraction. Members must be regular
files with relative paths under the intended root and no `..` component. Clean
extraction is verified against the same exact manifest, and the original release
is rechecked before the delivery PASS receipt is written. The receipt binds the
final archive bytes and manifest. The extracted manifest hash must equal the
original manifest hash.

No delivery blocker was found. The sealer is a Linux workspace packaging tool,
not a general validator for hostile ZIPs on every operating system. It does not
separately reject backslash or drive-colon characters in Linux filenames; the
release being assembled uses ordinary canonical relative paths. It should not
be advertised as a portable arbitrary-archive extraction service.

The sealer intentionally does **not** establish formal source-to-acceptance
binding. The parent must compare the packaged Lean sources, acceptance snapshot,
reviewed frozen hashes, runner, and receipt before sealing. Packaging integrity
alone cannot turn an unchecked or stale proof receipt into proof evidence.

## Formal gate engineering

The runner makes a new output directory outside both inputs, snapshots the exact
local import closure, configuration, controls, and its own source, and checks each
snapshot against the original before and after copying. Local Lean objects are
compiled into a fresh directory; existing project objects are not used. The
preserved generator source has an explicit fixed hash. The five formal target
modules compile with warnings treated as errors. Inherited local dependencies
also compile freshly but do not receive that extra warning flag.

All local closure sources are screened for active admissions, custom axioms,
unsafe/native bypasses, and selected kernel bypass options. The generated Lean
audit enumerates all environment constants attributed to the five targets,
including definitions and generated constants, and recursively checks their
axiom dependencies. It rejects unsafe/partial constants and any axiom beyond
`propext`, `Classical.choice`, and `Quot.sound`. Its parsed inventory must have
consistent counts, unique declaration names, and coverage of every target.
Module replay invokes `leanchecker` on all five targets. This remains replay by
the same Lean kernel with imported dependencies, as the receipt correctly says.

The final receipt binds source hashes, compiled object inventories, generated
auditors, declaration inventory, controls, command metadata and raw log hashes,
runtime endpoints, dependency revisions, cache resolution, and runner source.
Production objects and sources must remain unchanged through the controls and
replay. The runner catches failures and writes FAIL rather than a partial PASS.

The external compiled dependency cache is reused, not rebuilt. Runtime checks
authenticate every declared file except explicitly recorded mutable Git indexes;
the general runner does not claim that its runtime manifest excludes all extra
files. Direct external imports must resolve, by search precedence, to an object
in the pinned manifest with matching size/hash. As an additional read-only check,
this reviewer enumerated the actual nine external search directories: **11,381
`.olean` files, zero unmanifested `.olean` files, zero `.olean` symlinks**. See
`CACHE_OBJECT_INVENTORY.json`. This one-time filename inventory supplements the
runner's endpoint hashes; it is not a continuous runtime monitor.

## Cache correction and controls

The first integrated run, `centered_run01`, failed before any compiler command
because the old runner required an unused, absent `Cli` build directory. It must
remain recorded as FAIL. The corrected source records and omits absent build
directories while requiring every needed direct external import to resolve to
an authenticated cached object. The correction retains all nine dependency Git
pins and both declared-runtime checks. Its focused self-check resolved 40 direct
external imports and rejected an intentionally missing import. No theorem,
source, axiom, or negative-control obligation was removed by this correction.

The merged manifest contains 21 isolated controls: 8 positives, 12 intended
elaboration rejections, and 1 custom-axiom policy rejection. A negative control
needs a nonzero exit, an error diagnostic, and its required pattern. Timeout,
interrupt, missing import/object, unknown identifier, parser error, ambiguity,
resource exhaustion, or process-crash diagnostics do not count as intended
rejection. Controls are tied to exact snapshotted sources and raw logs.

The wrong-resolvent-sign control uses a broad `Type mismatch` pattern, but its
inspected source has one deliberate failing use: the established subtraction
inverse identity is supplied for a plus-sign goal. Its classification is valid
for these exact source bytes and compiler, not a freestanding semantic detector
for arbitrary changed tests. The other less-specific resolvent patterns likewise
have isolated, inspected failure sites. Placeholder rejection is intentionally
a strict compiler warning/error check. The custom-axiom module must first compile
successfully, then fail the separately generated policy audit; a syntax/import
failure in that module cannot stand in for forbidden-axiom detection.

The runner author's timeout self-check deliberately emits a matching rejection
diagnostic and then times out; the harness rejects that result. This is useful
evidence that timeouts cannot masquerade as semantic negative-control success.

## Outcome and limits

No blocking issue was found in the exact reviewed scripts or control manifest.
This report does not assert that the still-running `centered_run02` has passed.
Final acceptance requires its own complete PASS receipt and source/hash binding;
final delivery requires the sealer's clean-extraction PASS receipt. Mathematical
scope is established separately in `FROZEN_SOURCE_REVIEW.md`.

During this inspection, two assumed read paths were absent (a manifest under
`gate_tools` and a self-check directory spelled `selfcheck_03`); the actual
project manifest and `selfcheck03` were then read. Reading the not-yet-created
run02 receipt also correctly reported absence. These read errors did not run or
alter verification, and were not counted as successful checks.
