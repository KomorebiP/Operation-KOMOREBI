# Pinned runtime recovery

The runtime used for this checkpoint was restored from the stored archives `Lean_Compact_01.zip` through `Lean_Compact_05.zip`. Each contains one `.chunk` member. Concatenate the member bytes in numeric order, not the ZIP bytes themselves. The result is an XZ-compressed tar archive.

Expected length: **2,220,147,424 bytes**.

Expected SHA-256:

```text
f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7
```

The extracted directory is `Komorebi_Portable_Lean_4.34.0-rc2`. It contains `toolchain/bin/lean`, `toolchain/bin/lake`, and `workspace/.lake/packages` with the pinned cache. `provenance/runtime_recovery.json` records the checked part sizes and hashes from this execution.

Library retrieval identities, retained as metadata rather than filesystem paths:

| Part | File identifier |
|---|---|
| 01 | `file_00000000211881f590f83a9f9114f14a` |
| 02 | `file_00000000fe5081f58c57aeaedb580fbe` |
| 03 | `file_00000000e49481f5a027206c8809ea97` |
| 04 | `file_000000009e2081f59a298bc4f40f58db` |
| 05 | `file_00000000380081f595a22a760c9ccffb` |

In a fresh environment, check whether the files are already mounted before materializing Library files. Do not infer that a previous `/mnt/data` runtime persists. Missing `lean` or `lake` on PATH is not evidence that this stored runtime is unavailable.

The producing environment ran the unmodified compiler without the executable-location adapter. The replay runner intentionally does not silently substitute a different compiler or fetch newer dependencies. This checkpoint targets Linux x86-64, including a compatible WSL2 environment.
