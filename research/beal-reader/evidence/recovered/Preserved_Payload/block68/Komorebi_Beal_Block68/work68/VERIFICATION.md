# Reproduction and evidence boundary

Run from the extracted package:

    python -B verify.py --report ../Block68_Replay.json

The report MUST be outside the immutable package. Every one of the 13 new
scientific JSONs is deleted in a scratch copy and rebuilt. The generated
extended fixture is likewise deleted and rebuilt. Full JSON contents, all
payload hashes, the original predecessor bytes, and 19 named inherited source
leaves are checked. Backend availability flags may differ if NumPy is absent;
only these explicitly environmental fields are excluded from mathematical
comparison. The scalar fallback is slower and can require increasing
--job-timeout. A timeout is inconclusive, never a mathematical exclusion.

The standard library is sufficient. Optional NumPy executes exact bounded
int64 operations. Set BEAL_FORCE_STDLIB=1 to force scalar counting. The separate
count, column and sieve implementations import no primary arithmetic. The
backend-parity audit deliberately imports both counters and is not represented
as a third independent implementation.

Six diagnostic-specific negative controls alter a degree-two column, remove a
conductor factor, invent a common-polynomial pair, claim a false zero survivor
set, modify a point count, and modify a package payload. Each must fail for its
stated diagnostic. An unrelated import error or timeout is not acceptance.

The original Block67 verifier was separately run with --replay-predecessors
in this session, exited zero, and took 645.353 seconds. Its observed report,
log and exit record are preserved in verification/. That is not falsely
reported as a fresh historical replay in every default new-block invocation.
Add --replay-predecessors to execute the full selected chain again.

Final extraction/replay and archive-audit reports are external to the ZIP to
avoid self-referential hashes. They record actual command, status, timing,
software, regenerated output digests, negative-control results and limitations.
The computation manifest records development evidence separately from those
final execution records. No Lean compilation or external mathematical reviewer.

The development evidence manifest uses the documented version1 schema. Its
project validator (not an execution of the unmounted Mathbox validator) is:

    python -B work68/computations/validate_manifest68.py work68/COMPUTATION_MANIFEST.json --root .

It checks the populated contract and all declared input/output hashes. The
manifest reports the observed development replay, while the final fresh-ZIP
execution is a separate external record. No Git revision is invented.
