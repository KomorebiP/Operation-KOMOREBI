# Failures and corrections in this block

1. Runtime restoration: concatenating all seven uploaded offline parts succeeded
   and matched the pinned combined SHA256. An attempt to inspect the zstd stream
   with Python failed because `zstandard` was not installed. The installed `zstd`
   executable and GNU tar were used instead. The compiler and bundled libraries
   extracted successfully, and `lean --version` matched the requested pin.
2. The first Lean draft contained two incorrect *integer carry representatives*
   for the ordinary M action. Lean rejected both. Recomputing the row-matrix
   products gave carries -n2+m0 and -n0+3n2+2m0-7m2. Their residue actions were not
   changed. The rejected draft is retained as failed_explicit_descent_draft.lean.
   This was an incorrect draft identity, not a compiler or tolerance issue.
3. The same draft used the reserved token `section` as a definition name and had
   one unused simp argument. The definition was renamed `liftPair` and the
   unused argument removed. Warnings remained errors.

All final sources were subsequently compiled and audited from an isolated
build, then replayed from a fresh ZIP extraction. No gamma comparison was run,
no numerical near-zero residual was used as a proof, and no inherited full
Lean replay is claimed.
