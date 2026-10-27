# Compiler runtime evidence

Author: Komorebi P.

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, was downloaded from the official leanprover/lean4 release. The distributed compiler and kernel files were not modified.

The unmodified runtime could not locate its own executable: its numeric process path returned a permission error, while the current-process link was available. The attached app_path.c supplies that same self-location through /proc/self/exe, only for readlink calls naming the current process's own numeric executable link. It was compiled as a shared library and loaded with LD_PRELOAD. Other path requests and all proof checking were left unchanged. This adapter is specific to the producing environment and is not needed for normal Windows or Linux installations.

The attached controls use the real compiler. A valid arithmetic theorem was accepted with no axioms. A false arithmetic statement with an invalid rfl proof was rejected with exit code 1. These controls complement, and do not replace, the full source build and axiom audit.

No toolchain or mathlib binaries are included in the ZIP. Reproduction on a normal installation uses the pinned lean-toolchain, lakefile.toml, and lake-manifest.json.
