# Reproducing the diagonal formalization

## Exact environment

- Lean `4.34.0-rc2`, compiler revision `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- Preserve `lean/lean-toolchain` and `lean/lake-manifest.json`. All nine dependency revisions in the manifest were independently checked against clean local checkouts.
- This run used the official Linux x86-64 Lean archive with SHA-256 `3d011041203acacf300d343a39673f7d233743397993797c941346ae9e5df1a8`.
- Python 3 is required for the verification scripts; the normal verification scripts need only its standard library.

`records/FINAL_ENVIRONMENT.json` is the final environment snapshot. `records/ENVIRONMENT_ATTEMPTS.json` is a historical setup record containing intermediate states, including the initial absence of a compiler. It must not be read as the final verification verdict.

## Ordinary host

Install the pinned Lean toolchain through the standard Lean/elan workflow, or reuse an existing installation. From `lean/`, `lean --version` must report the version and compiler revision above. Allow Lake to obtain dependencies at the preserved manifest revisions; do not run an unpinned dependency update.

```sh
cd lean
lake exe cache get
lake build KomorebiSpaceDiagonal
cd ..
python3 scripts/verify_diagonal.py --native
```

The build target imports all seven new modules and their required existing dependencies. The subsequent script strictly elaborates each new module in dependency order with `-j1 -DwarningAsError=true -DautoImplicit=false`, checks the module-provenance axiom inventory, and runs the eight targeted diagnostic controls. It records before-and-after hashes for the production, inventory, and control-runner sources it checks. The individual control records contain their source hash taken after execution. A nonzero process exit or a detected source change stops the replay.

The source tree also exposes the original `KomorebiSpaceCombined` target. A bare `lake build` now requests both it and `KomorebiSpaceDiagonal`. The accepted continuation build log is for `lake build KomorebiSpaceDiagonal`; it is not a claim that the complete historical verification suite was rerun.

Replay scripts write new records and logs at their documented paths. To preserve the supplied historical evidence, unpack a second copy before replaying. Files ending in `_attempt_001`, recorded failed proof snapshots, and the original agent logs remain historical evidence rather than production imports.

## This execution host

The unmodified official Lean executable initially reported `failed to locate application`. Its runtime resolves its own executable via `/proc/<getpid()>/exe`; this host's process namespace does not expose that numbered path, although `/proc/self/exe` works. The failure, an unsuccessful `LEAN_SYSROOT`-only attempt, and a denied tracing diagnostic are recorded. No tracing restriction was bypassed.

`scripts/proc_self_exe_compat.c` defines one `readlink` wrapper. It delegates every call to libc, replacing only the exact own-process numbered executable pathname with `/proc/self/exe`. The official Lean executable, libraries, kernel, theorem sources, and compiled mathlib dependencies were not patched. The compatibility wrapper is part of the recorded execution environment and adds no mathematical axiom. Independent inspection checked its source, exported symbol, machine-code behavior, and positive and negative pathname probes. Forty-one selected installed official release files were compared byte-for-byte with the retained release archive, with no mismatch.

To reproduce this host-specific arrangement, put the extracted official compiler at the sibling path `.lean_runtime/lean-4.34.0-rc2-linux/` relative to the package directory. From the package root, compile the shim:

```sh
cc -shared -fPIC -O2 scripts/proc_self_exe_compat.c -o ../.lean_runtime/proc_self_exe_compat.so -ldl
scripts/lean_env.sh lean --version
cd lean
../scripts/lean_env.sh lake exe cache get
../scripts/lean_env.sh lake build KomorebiSpaceDiagonal
cd ..
python3 scripts/verify_diagonal.py
```

The sibling runtime layout is required only by `scripts/lean_env.sh`. The `--native` paths do not use it. The archive deliberately excludes the local `.lake` dependency symlinks and all compiler/cache binaries; a fresh checkout must obtain its own dependencies.

`scripts/provision_environment.py` is the retained historical provisioning attempt. It is not a supported installer: on this host its raw compiler-version check failed before the shim existed, and it is not idempotent for an already-existing mathlib directory. The commands above, rather than rerunning that historical script, describe the supported reproduction path. An earlier remote setup was abandoned; its recorded process had exited at reconciliation, and no remote proof output was accepted.

## Evidence boundaries

Kernel compilation verifies the encoded propositions in the pinned environment. The independent audits additionally check their match with the printed statements, the positive-coordinate index shift, actual Hilbert-vector constructions, exact constants, rounded schedule, and full real-budget quantification. The audits and strict replay refer to the final source hashes recorded in `records/COMPLETION.json`.

The parent publication is identified in `records/BASELINE.json`. Its historical declaration count and 44 diagnostic controls are not relabeled as fresh results. The current targeted inventory includes all new declarations, including compiler-generated helpers; it is not a count of new mathematical theorems.
