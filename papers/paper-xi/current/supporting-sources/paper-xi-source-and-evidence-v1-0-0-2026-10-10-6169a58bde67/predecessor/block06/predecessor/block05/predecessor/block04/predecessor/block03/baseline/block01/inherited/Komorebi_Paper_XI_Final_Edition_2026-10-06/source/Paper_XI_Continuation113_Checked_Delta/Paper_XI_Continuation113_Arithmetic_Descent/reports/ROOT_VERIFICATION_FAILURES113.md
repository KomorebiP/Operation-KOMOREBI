# Root integration failures retained

The first integrated replay compiled CyclicDefect113 but stopped before its
axiom audit. The new export parser incorrectly required all anonymous sections
to have explicit closing commands, although Lean permits a global anonymous
noncomputable section to end at EOF. This was a verification-harness error,
not a failed mathematical theorem.

The separate representation audit also found that a naive declaration regex
treated a doc-comment sentence beginning `theorem below` as an export named
`below`. The corrected root parser removes nested Lean block comments and line
comments while retaining string literals, and permits only anonymous sections
to remain at EOF. It then finds the actual76 named declarations.

The failed verifier is preserved as
evidence/final_replay/verify_new113_failed_snapshot.py, SHA-256
420deb811bf1d2b5ea97dfdccf7d114974ce38edcccf2897fa529d29bc75cc25.
The historical failed manifest pins that revision of scripts/verify_new113.py.
The current script differs intentionally; the snapshot is the recovery source
for the historical input hash. The failed run is not upgraded to a pass.

The corrected fresh replay is evidence/final_replay_corrected. It compiled
all four unchanged mathematical sources, audited76 explicit declarations,
and ran leanchecker on each new module. Its complete receipt and manifest
record the successful final run. The original280 baseline object files were
authenticated from110/111/112 archives and checked unchanged after the replay.
Those140 baseline modules and external Mathlib were reused, not rebuilt.

The arithmetic additive-character sign mismatch is a distinct mathematical
integration error, documented in LATTICE113 §8 and its preserved old snapshot.
It was corrected to the PLUS-trace convention used by the actual character
construction before the final arithmetic review. No original PDF or112
source/payload was altered.
