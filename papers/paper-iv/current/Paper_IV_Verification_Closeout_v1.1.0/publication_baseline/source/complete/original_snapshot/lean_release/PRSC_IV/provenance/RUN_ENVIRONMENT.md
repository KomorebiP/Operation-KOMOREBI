# Reproduction environment — v1.0.0

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d; Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine dependency revisions remain pinned. The optional executable-path shim supplies the known executable path in this runtime and changes no proof checker; ordinary installations do not require it.

Nine new modules add 57 mapped declarations. All 15 formerly partial records are closed. The warning-fatal integration build passes 3521 jobs. The live namespace audit covers 2234 declarations / 1999 theoremInfo declarations. All dependencies are restricted to the three disclosed standard axioms. The 43 existing semantic checks are retained.

Release checks cover exact name/kind resolution, aggregate manuscript associations, full namespace kernel dependencies, deterministic PDF reconstruction, fonts and structure, archive CRC/checksum/path parity, and a fresh extracted build with a revision-checked external dependency cache. The final archive contains no build caches.
