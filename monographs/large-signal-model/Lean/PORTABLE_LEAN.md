# Portable Lean verification

Use the restored compact kit assembled from Lean_Compact_01.zip through Lean_Compact_05.zip. Its Start package describes concatenating the chunk members and extracting the combined archive. The combined archive SHA-256 is:

`f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`

The required layout is `toolchain/bin/lean`, `toolchain/bin/leanchecker`, and `workspace/.lake/packages/` containing the pinned Mathlib dependency tree. This is a Linux x86_64 kit and also runs in x86_64 WSL2. Its full runtime check is `bash /path/to/kit/run.sh verify`.

The project checker takes `--kit /path/to/kit`. It needs no system Lean installation and does not download dependencies. When the unmodified compiler reports the specific “failed to locate application” startup error, the checker uses the kit's documented executable-path adapter. Other startup failures remain failures. The adapter is copied to a private temporary path so kit folders may contain spaces, and is removed when the check finishes.

The restored runtime passed its 16 supplied checks, including Mathlib import and rejection controls. This does not replace verification of this project's own proof sources.
