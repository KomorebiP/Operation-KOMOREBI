# PRSC X — residue counting continuation

This cumulative bundle continues `PRSC_X_Quantitative_Counting_Checked_Continuation.zip` (SHA256 `1f0091e84f7ac1311824413a30324f71ea0403d1b0d4785f6afd0914c9c9d2c2`). The source ledger remains **17 checked / 3 partial**.

The principal new arithmetic result is a power-saving estimate for actual ideal norm-character sums in a fixed class, under an explicit residue-unit witness and nonvanishing on a supplied inverse-class representative. Finite-mean cancellation, sign-sensitive lattice counting, and the exact weighted generator-to-ideal correspondence are proved dependencies. `CURRENT_STATUS.md` states the theorem's precise scope and the remaining obligations in the paper.

The bundle includes cumulative Lean sources, frozen predecessor and new proof objects, exact manifests, the mathematical addendum, independent audit records, compiler controls, and retained failed attempts. `verification.json` is the definitive verification record. Historic status files are retained under `evidence/baseline`; they describe earlier checkpoints.

## Reproduction

Use the pinned Komorebi portable Lean 4.34.0-rc2 kit and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

    python3 checks/replay_residues.py /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2

This verifies all delivered source/object hashes, seeds a fresh build directory with the frozen predecessor objects, and compiles every new module in dependency order with warnings treated as errors. It imports no delivered new proof object. It checks named declarations' transitive axioms. Once compilation starts, it retains a new directory of logs, including failed compiler attempts. It does not rebuild all predecessor modules.

For a file-integrity check without invoking Lean:

    python3 checks/replay_residues.py --verify-only

The independent audit separately checks every environment declaration owned by the new modules, including generated declarations. Archive extraction and hash verification are file-integrity checks; they are not an additional compiler replay. No full cumulative rebuild is claimed for this continuation.

## Completed verification

All 34 new modules independently compiled with warnings treated as errors and reproduced identical proof objects. They add 156 theorem/lemma declarations. The transitive axiom audit covered 319 owned declarations, including generated declarations; only the standard three Lean axioms occurred. One positive control passed, three false claims were rejected at the intended contradiction, and the placeholder was rejected specifically for using sorry. All 221 predecessor sources and proof objects retain their exact hashes. This continuation does not claim a full cumulative rebuild.
