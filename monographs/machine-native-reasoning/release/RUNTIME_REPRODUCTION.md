# Reproduce the pinned offline proof environment

Use the saved `Lean_Compact_01.zip` through `Lean_Compact_05.zip`, not a newer
online compiler. These are separately stored user runtime parts and are not copied
into this source delivery. Place the five ZIPs in one directory and run:

```sh
python3 tools/restore_runtime.py --parts /path/to/parts \
  --out /path/to/Lean_Portable_Compact.tar.xz \
  --extract-to /path/to/runtime-parent
```

The tool verifies every chunk and the complete archive before extracting. It
refuses an existing output file or a nonempty extraction directory and requires
Python's `tarfile.data_filter`. The actual combined archive is 2,220,147,424 bytes,
with SHA-256
`f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.
In this continuation the helper assembled and extracted all 166,035 members.
The actual restoration receipts are under `evidence/runtime19/`. The helper code
is byte-identical to the predecessor and its earlier 28-fixture validation remains in historical evidence. The current gates rerun 20 verifier tests and 10 snapshot/comparison tests. This does not prove arbitrary Python executions correct.

The runtime root is
`runtime-parent/Komorebi_Portable_Lean_4.34.0-rc2`. Its compiler is Lean 4.34.0-rc2,
commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned to
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, alongside eight other pinned
repositories. The cumulative gate verifies all nine revisions, the compiler
identity and the actual imported proof-cache artifacts against the retained
runtime inventory. It does not rebuild those dependencies or independently attest
their origin. The runtime is Linux x86-64; native Windows execution is not claimed.

## Verify the delivered source before building

```sh
python3 tools/verify_package.py
python3 scripts/supervise.py \
  --runtime /path/to/runtime-parent/Komorebi_Portable_Lean_4.34.0-rc2 \
  --out evidence/my_replay --whole-timeout 1800
```

Choose a new output directory. A run adds files to the working tree, so the immutable
package integrity command is intended before generating those new outputs. An
independent extracted-source replay must use a separate source directory with no
preexisting project objects. Run the primary and extracted gates sequentially.
`evidence/CORE32_FROZEN_SOURCE.zip` contains the exact proof-gate source inputs
without compiled project objects. It is a source snapshot, not a full distribution.

Each compiler invocation has one worker, warnings as errors, a 4096 MiB internal
limit and a 45-second wall limit. Every other gate command retains the 45-second
wall bound. The supervisor has a 1800-second total bound. These limits may be
unsuitable for slower hosts. A timeout must remain a failed execution rather than
being relabeled as a logical rejection or a successful proof run.

## Compare completed fresh runs

After both runs terminate successfully, use the supplied comparison script:

```sh
python3 scripts/compare_rebuild.py \
  --final /path/to/primary/evidence/my_replay \
  --fresh /path/to/extracted/evidence/my_fresh_replay \
  --snapshot /path/to/CORE32_FROZEN_SOURCE.zip \
  --out /path/to/comparison.json
```

The comparison also checks the source tree containing that script against the
receipts. Every production object must be byte-identical; a generated nonproduction
audit helper may differ only under the explicitly recorded helper boundary. Its
source and complete axiom records must still agree. This release includes the current final19/fresh19 proof objects. Earlier compact predecessor objects remain omitted and inventoried as historical omissions.

## Adapter on this host

The direct compiler startup failed with `failed to locate application`. Both accepted gates used the distribution’s preserved `compat/app_path.so` through `LD_PRELOAD`. This adapter supplies executable-path discovery for the host; no proof-kernel modification was made. Example:

```sh
LD_PRELOAD="$KOMOREBI_LEAN_RUNTIME/compat/app_path.so" python3 scripts/supervise.py --runtime "$KOMOREBI_LEAN_RUNTIME" --out evidence/my_new_replay --whole-timeout 1800
```
