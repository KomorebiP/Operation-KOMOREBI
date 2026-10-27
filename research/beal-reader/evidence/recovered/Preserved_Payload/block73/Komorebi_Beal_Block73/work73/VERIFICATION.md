# Verification and evidence scope

Production uses the Python standard library, with bytecode disabled. Run

    python -B verify.py --report ../Block73_Replay.json

The verifier checks the exact payload member set and all hashes, the original
Block72 bytes, and eight inherited leaves through nineteen archive levels.
It copies the package to a clean temporary directory, checks the recorded input
and output hashes, deletes BOTH scientific JSONs, and rebuilds both with separate
arithmetic implementations. Every field and byte hash must agree.

Seven altered scientific certificates must be rejected for their exact changed
field: a false883 seventh power, an invented mod343 lift, zero tame defect, false
elimination of the eight patterns, a free uniformizer direction, all upper shifts
admitted, and zero fixed-seven valuation. An eighth test corrupts README and must
be rejected by the package hash checker. These controlled failures are not failed
scientific runs. The 49-correction matrix control has a universal expansion proof;
the coordinate-direction tests are not misreported as enumeration of all next digits.

--integrity-only runs no science. --replay-predecessor additionally runs the
immediate Block72 DEFAULT verifier, not the full nested history. Reports must be
outside the immutable archive. Per-command wall limits are180seconds, or300 for
the immediate predecessor. No memory limit is claimed as enforced. Programs are
single-threaded and deterministic.

COMPUTATION_MANIFEST.json records the actual development commands, software,
arithmetic domains, scope, before/after source hashes, result/log hashes and
runtimes. It uses schema2 and is checked by explicit PROJECT-LOCAL field/hash
validation. No claim of execution of the separate plugin manifest validator is
made. Final fresh-extraction replay and archive audit are external to avoid a
self-referential checksum claim.

The new computations establish finite assertions, not the global Galois/Frey
hypotheses or exclusion of any of the eight patterns. No new point counts,
Lean compilation, or independent mathematical review.
