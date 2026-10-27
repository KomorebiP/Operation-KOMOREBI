# Development failures and retained replacements — v0.4

This file distinguishes environment, implementation and proof-draft failures from
mathematical counterexamples. The accepted outcomes are generated in RESULTS.md.

## Runtime restoration

The initial runtime path had no usable Lean executable. Five retained compact
parts were materialized and hash-checked. The combined archive is XZ-compressed
tar, despite a `.tar.zst` local filename. An initial attempt to use an unavailable
Python zstandard module failed. Streaming container execution was unsupported.
A whole-archive extraction timed out. Stateful XZ/tar extraction then completed
in bounded batches; a permission mismatch between root and the Python user was
corrected. `evidence/ENVIRONMENT.json` records the actual restored versions and
source pins. The failed restoration attempts are not compiler verification.

## Proof drafts and module integration

Early MatrixLinearBridge drafts had namespace/API issues, divisibility-witness
orientation errors, and an unused simp argument. They were corrected before the
accepted compiled proof. A large-instance application initially mixed a ZMod
binder with the predecessor's literal Fin ring; this was corrected. The small
nonlinear counterexample initially exhausted the default recursion limit; its
finite local check was rerun with an explicit larger limit.

The legacy Std files could not be efficiently mixed with Mathlib through broad
legacy imports. All 213 predecessor files received a mechanical module/public
import/exposed-section header migration, with the original bodies preserved.
The original ZIP remains frozen. This is a source migration, not byte identity of
the current `.lean` files; literal matrices and proof bodies are unchanged.

The first combined 202-theorem instantiation file exceeded its per-task limit of
180 seconds. It did not report a false mathematical statement. Its partial cold
run and timeout are retained in `evidence/UNSPLIT_CHECKPOINT.json` and
`evidence/UNSPLIT_RUN_FAILED.log`. That run is not counted as the final cold audit.

Splitting the file into 13 small batches was not by itself sufficient to remove
expensive repeated arithmetic-instance conversion. A generic Fin/ZMod wrapper
then failed to identify Std's `Lean.Grind.Semiring` with Mathlib's induced one.
Several drafts exposed differences in the bundled numeral/scalar operations and
rewriting instance selection. `FinRingCompatibility.lean` proves the instance
agreement from its actual operation fields and laws. The corrected generic
wrapper reuses that proof. The first 16-instance batch then compiled successfully
in the retained development check. All batches belong to the separate final cold
run, whose accepted hashes are fixed.

Logs named `*_attempt*.log`, `*_wrapper*.log` and the compatibility logs retain
those diagnostics and the accepted replacements. Scratch debug files were not
accepted library sources and are not counted as proved declarations.

## Mathematical scope boundary, not an error

The example `(x,y) -> (8x,8y)` over Z/16 requires two coordinates for a LINEAR
initial encoding. A nonlinear parity packing uses one residue. Both statements
are proved, together with nonadditivity of that packing. This refutes dropping
the linear-initial-encoding hypothesis, not the stated minimum theorem.

## Final versus partial evidence

No interrupted or timed-out run is a PASS. The final cold run starts with a new
empty local build directory and its own source hashes. The later extracted-copy
replay is separately scoped; it must not be described as another full rebuild of
all generated modules unless its task record actually contains that rebuild.

## Provenance-scope check

The first migration provenance list included two new modules alongside the 213
actual parent files. A parent-only archive comparison detected that scope error.
The initial failure record is preserved; the corrected migration record contains
only the 213 parent files, whose mathematical bodies are unchanged. No accepted
Lean proof source changed in this metadata correction.

## Distribution name correction

The first packaging helper treated the `.4` version segment as a filename suffix
and named the outer ZIP `v0.zip`. Its payload checks passed, but the requested
versioned filename was wrong. The filename construction was corrected, the final
archive rebuilt as v0.4, and its extracted integrity/Python checks rerun.
