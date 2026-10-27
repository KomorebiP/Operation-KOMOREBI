# Pinned runtime provenance

This release uses the already acquired official Lean 4.34.0-rc2 Linux toolchain, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Compiler binary SHA256 is `e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550`. The official release archive has 580281129 bytes and SHA256 `3d011041203acacf300d343a39673f7d233743397993797c941346ae9e5df1a8`. Exact archive-member hash checks for the compiler and kernel shared library were completed when this runtime was assembled for the Quadratic-Form/K-COS companion; their provenance is retained in runtime_hashes.json. The failed Library multipart retrieval was not used.

Mathlib is commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Its matching public cache supplies dependency objects, while every selected H12 project module is freshly compiled from the archived source bytes.

The producing environment lacks the numeric `/proc/<pid>/exe` executable symlink. The unchanged, narrow attached `app_path.c` adapter maps only the current process's own executable-link read to `/proc/self/exe`; it is loaded through `LD_PRELOAD`. The compiler and proof kernel were not modified. Normal Lean installations require no adapter.

The runtime and dependency caches are not included in the portable publication package. The final verifier uses POSIX wait4 for actual per-process peak resident-memory accounting. Initial attempts without that measurement are marked explicitly; no retrospective peak RSS is fabricated.
