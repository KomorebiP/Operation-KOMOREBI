# Fresh unchanged-source verification

The current replay uses the unchanged Komorebi Space 1.15.0 mathematical sources,
control sources and integrated runner. All 229 formal input hashes match the
accepted predecessor receipt. The authoritative outcome is `run01/receipt.json`;
a running or failed receipt is not an accepted proof run.

The exact source archive is `Komorebi_Space_Publication_v1.15.0.zip`, SHA-256
`7f68336e652bc6af817ba0fc8c96476f7cc39318ff333f404e202f4388dfe63f`.
The working copy has no inherited project proof objects. Its only environment
addition is `lean/.lake/packages`, a symlink to the previously restored pinned
external dependency cache. That symlink is an environment setup detail and must
not be shipped as project source.

## Offline reproduction on the pinned Linux runtime

Set `KOMOREBI_LEAN_RUNTIME` to the restored
`Komorebi_Portable_Lean_4.34.0-rc2` directory. The five compact runtime parts
reconstruct an archive with SHA-256
`f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.
The runtime is external to the publication. Its Linux binaries can be used in an
appropriate Linux environment such as WSL; this replay is not a native Windows
qualification.

In a separate working copy of the publication, provide the pinned external
packages at `lean/.lake/packages`. For the saved portable runtime, this is its
`workspace/.lake/packages` directory. Do not overwrite an unrelated package
directory. The integrated runner checks all nine dependency revisions and rejects
tracked changes.

From the working publication root, choose a new output directory outside it:

```sh
PATH="$KOMOREBI_LEAN_RUNTIME/toolchain/bin:$PATH" \
LD_PRELOAD="$KOMOREBI_LEAN_RUNTIME/compat/app_path.so" \
python3 -B verification/runner/runner.py --output /absolute/path/new-verification
```

The shipped executable-path adapter is needed on this host. It is inherited as
an external environment wrapper and its actual bytes are included in the
runner's runtime inventory. No compiler, project proof or verifier source is
modified. A normal compatible Linux installation can run the same verifier
without this host-specific environment wrapper.

The unchanged runner compiles sequentially with one Lean worker, warnings as
errors, and automatic implicit binders disabled. It retains its default
300-second per-command and 1800-second declaration-audit limits. It imposes no
new fixed memory cap. Failed and interrupted attempts are retained; each retry
requires a new output directory.

The gate includes all 166 project targets, the recursive axiom inventory and
56 mixed diagnostic controls. Those controls are 18 expected acceptances,
35 expected elaboration rejections and three axiom-policy rejections. They must
not be described as 56 compiler rejections. Mathematical scope remains the
16 principal groups and the separately documented source correspondence.

## Evidence boundary

`RUN01_SETUP.json` records the setup and exact initial formal inputs. The actual
runner receipt records every command, compiler and dependency revisions,
source snapshots, objects, logs, exported declarations and controls. The runtime
snapshot records compiler and installed-cache bytes at both endpoints. Installed
external caches are reused, not rebuilt or independently authenticated by this
procedure. Endpoint identity cannot exclude a transient change restored before
the final check. This is a compiler/kernel check, not an independent kernel or a
new whole-book semantic review.
