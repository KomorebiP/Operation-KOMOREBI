# Continue from AVOC v0.41.0

Use this cumulative checkpoint. Read PROOF_BOUNDARY.md, GAP_LEDGER.md,
FORMAL_THEORY.md, RECORDER_EXECUTABLE.md, and the v0.41 verification/failure records.
Its exact predecessor is AVOC_Formal_v0.40.0.zip, SHA-256
bf0b87a381ac47e4de215c0cfbcde4e3fcfa710470390e4db8843cb4140e739f.

The lifecycle block now proves global operation-ID invariants and a full
source-generative recorder-to-reveal refinement. The final calibrated policy
reads actual terminal samples and denies issuance for rejected runs, any pending
operation, or insufficient selected checkpoints. Its error bound is unconditional.

Do not confuse this with a physical provider or universal Python/storage
refinement. Raw terminal labels are supplied; generative labels are constructed.
The log is ordered by completion. Outcome-dependent completion order can bias
fixed prefixes even after every intent is resolved. Preserve the exact
completion-order, censoring, and completion-conditioning counterexamples.

The next statistical target is a precise multi-attempt model that justifies the
accepted/report-order source law, or an alternative initiation-indexed sample
contract that blocks biased omission/reordering. It must handle incomplete and
replayed operations without automatic retries or hidden conditioning. A separate
next controller target is finite multi-episode error/reward/accounting composition.

Keep exact identity strata, fixed schedules, frozen per-episode quote bands,
conservative reservation accounting, and all previous proof boundaries. The
new recorder is a pure snapshot reducer; no durable host migration or actual
paid operation was performed. The old calibration format is unchanged.

Preserve inherited sources and historical evidence. Rebuild using Lean 4.34.0-rc2
and nine exact package pins, audit exact theorem names, run substantive negatives,
retain failures, compare actual Lean/host results, then verify and save the full
cumulative package. REPRODUCE.md supplies the commands.
