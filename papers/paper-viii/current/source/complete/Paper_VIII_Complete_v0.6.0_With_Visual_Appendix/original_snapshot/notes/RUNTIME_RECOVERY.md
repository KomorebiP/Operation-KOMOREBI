# Fourth-block runtime recovery

The supplied offline parts were restored with the original starter assembler. All seven part SHA-256 checks and the combined archive SHA-256 passed. The combined archive hash was:

`66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`

The recovered compiler reported Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. The cumulative verifier checked both the manifest and actual Mathlib repository HEAD against `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, then compiled all 23 active modules.

An initial request for an unsupported interactive streaming session failed before starting the assembler. A noninteractive process was used successfully instead. Its complete assembly log is retained in `verification/fourth_runtime_recovery.log`. Archive hashes alone were not treated as proof-checking evidence.

The earlier recovery record is preserved in `verification/prior/third_block_RUNTIME_RECOVERY.md`.
