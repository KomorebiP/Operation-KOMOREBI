# Producing runtime and recovery

The pinned official Lean 4.34.0-rc2 Linux archive was downloaded from:
https://github.com/leanprover/lean4/releases/download/v4.34.0-rc2/lean-4.34.0-rc2-linux.tar.zst

Archive size: 580281129 bytes.
Archive SHA256: 3d011041203acacf300d343a39673f7d233743397993797c941346ae9e5df1a8.
Compiler commit: 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib revision: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

The first requested runtime retrieval used the existing seven-part offline kit.
Fresh preparation succeeded, but byte downloads returned HTTP 403. No kit part
was downloaded, so no kit-part or combined-kit verification is claimed here.
The public official compiler release supplied the alternative runtime.

Initial tar extraction reported ownership metadata errors. Extraction was
retried with --no-same-owner. A static compiler library remained truncated and
caused a cache-executable linker failure; streaming that exact official archive
member to the library restored its full bytes and expected hash. The cache
was initially obtained through Lean's --run interpreter. The final compiler
binary, shared proof-kernel library, and restored static library match their
corresponding official archive members byte for byte. The distributed compiler
and proof kernel were not edited.

This managed environment could not resolve the compiler's numeric-process
executable link. The attached app_path.c redirects only the current process's
own /proc/<pid>/exe readlink call to /proc/self/exe. It does not change other
path requests or proof checking. It was reused unchanged from the preceding
Signal companion and compiled as a shared LD_PRELOAD adapter. Normal Lean
installations do not need this adapter.

Fresh final validation used lake build, direct source checks for both
mathematical modules and the root import, #check and #print axioms for all
34 declarations, an accepted axiom-free arithmetic control, and two rejected
negative controls. Exact commands, exits, source hashes, and evidence hashes
are recorded by verification/BUILD_AUDIT.json.

Prior failed project build logs record import selection, section-variable
syntax, and proof-expression normalization errors resolved before the final
successful checks. No proof admission was introduced.

Compiler and mathlib dependency binaries remain outside the publication ZIP.
The portable lake-manifest.json uses git URLs and exact revisions; its scratch
cache symlinks are not deliverables.
