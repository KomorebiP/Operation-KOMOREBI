# Reproduction

## Pinned dependencies

Lean: leanprover/lean4:v4.34.0-rc2

Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06

The complete dependency manifest is included. The source archive does not contain the compiler or Mathlib cache.

## With the existing portable runtime

From the project root, with KIT pointing to Komorebi_Portable_Lean_4.34.0-rc2:

```bash
bash "$KIT/run.sh" attach "$PWD"
export PATH="$KIT/toolchain/bin:$PATH"
python3 scripts/verify.py --clean
```

The attachment script checks exact dependency revisions. It creates local dependency symlinks and does not alter the mathematical sources.

## With an independently installed pinned Lean toolchain

Make the pinned dependencies available using Lake and the included manifest, then run:

```bash
lake build Komorebi
python3 scripts/verify.py --clean
```

The verifier's --clean flag deletes only this project's .lake/build. It does not delete Mathlib's shared cache. It re-elaborates all active mathematical source files with warnings as errors, prints every theorem's axiom dependencies, checks for prohibited source shortcuts, runs compiler negative controls, and compares input hashes before and after.

Expected final status is PASS. Expected rejected controls are a false proof and an intentional placeholder. A rejection must match the intended compiler diagnostic, not merely return a nonzero status.

The generic verification timeout is 240 seconds per compiler command. It is a resource limit on this execution procedure, not a bound on the mathematical theorems.

## Integrity

SHA256SUMS.txt records the distributed files. verification/RESULTS.json records proof inputs before and after the final run, exact commands, compiler return codes, durations, and the observed axiom set. verification/runtime_restore.json records all seven compressed runtime-part checksums and the reconstructed stream checksum.

Historical failed attempts are kept for audit. Only verification/RESULTS.json is the final active verdict.
