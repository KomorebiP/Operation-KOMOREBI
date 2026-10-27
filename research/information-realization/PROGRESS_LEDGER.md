# Progress ledger
## Information Realization v0.4.0 — Lean block 1

**Completed 15 October 2026.** First actual Lean formalization of the v0.3 information-realization continuation.

### Authoritative predecessor

`prior/komorebi_information_realization_v0_3.zip` is retained unchanged.

SHA-256: `7f4c5b332982bae97ae6415a8fac9ab980b026187953b9da457169214b211dbf`.

Its original Python, paper proofs, Haar wheel, source provenance and earlier reports remain historical evidence. This block did not rerun all v0.3 Python suites or claim they were formally ported.

### Runtime actually recovered and run

Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Linux x86-64.

The runtime was absent from PATH at entry. Direct curl to GitHub failed DNS resolution. The user's seven `Lean_Offline_01.zip` through `Lean_Offline_07.zip` parts were recovered from Library. Each contains one chunk. Concatenating chunks in numeric order gives a 2,896,789,714-byte Zstandard tar archive with SHA-256:

`66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`.

This matched the recorded prior runtime hash. It was extracted and the compiler and Lake versions were actually executed. The current-session kit path was `/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2`; it is a session path, not a promise that another session will already contain it. The large runtime is not embedded again in this release.

### Completed formal block

58 named theorem declarations in six modules. Counts: Foundations 13, LinearAccess 9, OptimalRepair 4, Dimension 2, Predictive 13, Haar 17. All proofs pass with warnings as errors. Every theorem has a live axiom audit. Only the three allowed standard axioms occur; 16 declarations have none. No production proof uses a placeholder, custom axiom, native decision shortcut or unsafe implementation escape.

### Release gates

1. `reports/clean_run_02`: clean serial rebuild, all axiom audits, all five strengthened negative controls.
2. `reports/archive_replay`: same checks from a separate extracted source archive, with no source-tree object files inherited.
3. `DELIVERY_CHECKS.json`: archive member checksums and predecessor hash.

### Exact next restart point

Begin from `lean/KomorebiInformation/Dimension.lean` and `OptimalRepair.lean`. Expose a finite basis of the obstruction subspace to translate the already-proved optimal message map into a d-row matrix. Then add a typed matrix-certificate importer and a theorem connecting its finite check to `repair_certificate_sound`. Use the preserved v0.3 certificate output as data, not a theorem assumption about its correctness.

The following block should port the finite linear closure algorithm and its bound on strict enlargements, using the already-compiled all-word simulation and canonical quotient results. Probability/entropy identities remain a separate later block. The full obligation inventory is in `FORMALIZATION_LEDGER.md`.

### Do not lose these boundaries

Classical existence of a linear repair does not verify the Python encoder-generation algorithm. Kernel-checked Haar identities do not verify the native floating implementation or physical noise robustness. An all-time simulation identity does not by itself prove termination/minimality of the row-space closure implementation. Proofs of recovery are pointwise; no prior is silently introduced.
