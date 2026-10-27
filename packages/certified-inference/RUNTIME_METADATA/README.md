# Komorebi P. Portable Lean: full compact edition

This edition preserves **every byte of the original extracted bundle**. It uses
stronger lossless compression. No Lean, Lake, mathlib, native compiler, cached
proof, source, license, or other file has been removed.

- Previous compressed archive: 2.897 GB.
- Compact archive: 2.220 GB, a **23.4% reduction**.
- Extracted directory: about 11 GB, unchanged.
- Download parts: 5. Allow 20 GB free space during assembly and extraction.

Download Lean_Compact_01.zip through Lean_Compact_05.zip into one folder.
Extract this starter ZIP into the same folder. Keep the part ZIPs intact.
Open a Linux or WSL terminal in that folder and run:

```bash
python3 assemble.py --extract
```

Assembly uses Python 3.9+ standard libraries. Extraction uses tar and xz (the xz-utils package).
If the ZIPs are elsewhere, add `--parts /path/to/downloads`. To check all parts
without creating another archive, use `--verify-only`.
The assembler checks ZIP CRCs, every part hash, and the combined SHA-256.
Existing output archives and extraction folders are not overwritten.

The assembled archive is `Lean_Portable_Compact.tar.xz`. Its uncompressed tar data has exactly
the same SHA-256 as the original bundle. See COMPRESSION_REPORT.json.
Sixteen fresh Linux runtime checks passed, including full import Mathlib,
the PRSC VI algebra example, and rejection of a false theorem and a placeholder.
See RUNTIME_CHECKS.json. The earlier 23-check report remains inside the bundle.

Inside the extracted `Komorebi_Portable_Lean_4.34.0-rc2` directory:

```bash
bash run.sh verify
bash run.sh check workspace/PortableCheck.lean
```

This is the same Linux x86_64 runtime, also intended for x86_64 WSL2. It requires
Bash, Python, Git and a compatible glibc Linux environment. It is not a native
Windows runtime. The separate native Windows setup kit has not been changed.

Lean and Lake remain pinned to 4.34.0-rc2. Mathlib remains pinned to
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, with all nine dependency repositories.
The original README inside refers to the earlier archive filename and download
size. Use this outer README for the new archive's filename and assembly steps.
All original launch, proof-checking, and cache-attachment instructions still apply.

This changes packaging only. It does not claim to finish any remaining PRSC proofs.
