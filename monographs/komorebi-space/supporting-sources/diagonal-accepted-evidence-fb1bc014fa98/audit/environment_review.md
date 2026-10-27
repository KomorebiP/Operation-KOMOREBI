# Independent environment and reproduction review

Scope: read-only review of the host adapter, pinned Lean/mathlib identity, historical provisioning, and package instructions. No installer, cache bootstrap, or broad dependency build was rerun. The accompanying JSON contains actual command arrays, outputs, source hashes, and binary comparisons.

## Result

The recorded compiler environment checks out. The installed host adapter makes the documented narrow pathname substitution; no compiler or proof-kernel binary modification was found. The new diagonal build entry was fixed during review; the remaining reproduction-documentation actions below are being handled by the parent agent. This review does not re-audit the mathematical proofs.

- `lean --version` under the wrapper reports Lean `4.34.0-rc2`, compiler commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- `lean --print-prefix` reports the expected sibling `.lean_runtime/lean-4.34.0-rc2-linux` installation.
- All nine checked-out dependency HEADs equal the exact commits in `lean/lake-manifest.json`; their working trees are clean. Mathlib is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- Forty-one release files were compared byte-for-byte by SHA-256 with the retained official release archive: every release executable under `bin/`, every shared library under `lib/`, and the `Init.olean`, `Lean.olean`, and `Lake.olean` roots. All match. This covers the compiler and loaded proof-kernel shared code; it is not a claim that every release file was independently compared.
- Retained archive SHA-256: `3d011041203acacf300d343a39673f7d233743397993797c941346ae9e5df1a8`.
- Shim source SHA-256: `de6b1d4743f635590a2461493cdb0303abd022ef91dad2d833d7f50fbaa670b7`, matching `ENVIRONMENT_ATTEMPTS.json`.
- Installed shim SHA-256: `a12d70e92c1c016ccb90589cdb5675a909729f4a775feebffcdb7f0dc6551992`.

Archive provenance is the retained download from the recorded official release URL; no separate upstream signature was checked. The inherited `LD_PRELOAD`, `LEAN_SYSROOT`, and `LEAN_PATH` variables were unset before invoking the wrapper.

## Adapter behavior

The source defines only an interposed `readlink` function. It computes the caller's own `/proc/<getpid()>/exe`, compares the full input pathname using `strcmp`, and delegates to the original libc `readlink`, preserving the buffer and length. Only exact equality changes the delegated path to `/proc/self/exe`. There is no prefix matching, filesystem mutation, compiler/kernel hook, or general redirection of other processes' executable paths.

The installed library's exported symbols and `readlink` disassembly agree with this implementation. Four dynamic cases were checked, both without and with the wrapper:

| Path form | Without wrapper | With wrapper |
| --- | --- | --- |
| Own numbered `/proc/<pid>/exe` | `ENOENT` | Same executable as `/proc/self/exe` |
| `/proc/self/exe` | Correct executable | Same correct executable |
| Own numbered path with trailing `/` | `ENOENT` | `ENOENT` |
| Non-own numbered executable path | `ENOENT` | `ENOENT` |

This is a host runtime adapter, not a proof axiom. The on-disk Lean executable and shared libraries remain unchanged. The wrapper sets the pinned executable path and sysroot, then uses `exec`; it also propagates the preload to child processes. An ordinary matching host can use Lean and Lake directly.

## Required reproduction instructions

1. Treat `scripts/provision_environment.py` as the preserved historical first attempt. On this host its unwrapped version probe still explains its recorded failure. It neither builds the adapter nor obtains the cache nor connects the project dependency directory. Its `mathlib` directory creation is not idempotent. It should not be advertised as a current end-to-end installer.
2. Preserve `ENVIRONMENT_ATTEMPTS.json` as history, but identify a separate final environment snapshot as authoritative. Its old `local_compiler: not installed` and `formal_compilation_passes: 0` fields otherwise conflict with its appended successful observations.
3. Resolved during review: the parent added `lean/KomorebiSpaceDiagonal.lean`, which imports the diagonal theorem and asymptotic modules, and registered it both as a library and a default target beside the unchanged `KomorebiSpaceCombined` target. The exact continuation command is now `lake build KomorebiSpaceDiagonal`. The earlier observation that the default target omitted the continuation is historical, not a defect in the updated configuration.
4. Document the exact host-only shim compilation, its sibling runtime layout, and the normal-host alternative. A suitable command from the package root, once the matching runtime directory exists, is:

   ```sh
   cc -O2 -fPIC -shared scripts/proc_self_exe_compat.c \
     -o ../.lean_runtime/proc_self_exe_compat.so -ldl
   scripts/lean_env.sh lean --version
   scripts/lean_env.sh lean --print-prefix
   ```

   This command is a reproduction recommendation, not a claim that a rebuild was performed during this review. Shim binary hashes can differ with the C compiler; the audited source hash identifies its behavior.
5. Do not package the current `.lake` directory as portable dependencies: the current mathlib entry is an absolute symlink into this scratch runtime. Preserve the pinned manifest and reconstruct dependency checkouts/cache on the recipient host.
6. The inspected control runner hardcoded the host wrapper. The parent has announced a `--native` mode as the resolution; it was not yet present in the read-only follow-up snapshot. Confirm that option before documenting ordinary-host control reproduction.

With the usual Lean/elan setup on a normal host, the intended sequence is to install the exact toolchain named by `lean-toolchain`, enter `lean/`, run `lake exe cache get`, and build `KomorebiSpaceDiagonal`. Verify the reported compiler revision and retain the manifest. A direct final check should use the recorded `lake env lean -j1 -DwarningAsError=true -DautoImplicit=false` flags against the continuation entry and axiom/control audit files. A successful build of only the historical `KomorebiSpaceCombined` target remains insufficient evidence for the new diagonal work.

No cache rebootstrap is needed to validate the present run. The current pinned environment was independently inspected and its narrow host behavior reproduced.
