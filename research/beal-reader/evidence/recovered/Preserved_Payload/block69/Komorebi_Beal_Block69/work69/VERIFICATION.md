# Reproduction

    python -B verify.py --report ../Block69_Replay.json

The report is external to the immutable package. All16 new scientific JSON
outputs and the generated fixture are deleted in a scratch copy and rebuilt.
Primary and separate counts are run for each of the five declared test primes.
At most two count jobs run concurrently. All new outputs are compared byte
for byte via SHA256; they are deterministic exact-integer data.

Seven diagnostic-specific corruption tests alter a degree-two column, omit a
conductor, claim zero survivors, inflate the support minimum, invent a common
polynomial pair, alter a point count, and modify a payload. An import error or
timeout does not count as the expected rejection.

The exact Block68 source archive and ten named immediate members are checked,
along with six byte-for-byte copied core/input mappings. The included observed
Block68 default replay took104.976 seconds and returnedPASS_DECLARED_CHECKS.
It is distinct from a new --replay-predecessors invocation, which requests the
full selected historical chain. Existing older logs are retained as history.

Python3.10+ and its standard library suffice. Optional NumPy only vectorizes
bounded exact int64 modular operations. BEAL_FORCE_STDLIB=1 selects scalar
counting; increase --job-timeout for that slower backend. A timeout is always
inconclusive. The new primes are<=1709; a conservative bound50*1709^3<3*10^11
covers the raw integer polynomial intermediates and is far below2^63.

The independent engines do not import primary arithmetic. The new secondary
refiner uses coefficient theta^2=theta+1, rather thanw^2=5, and reconstructs
correction pairs from their trace/norm. Its input94-cover is the same pinned
predecessor theorem certificate, freshly replayed, not independently invented.

The final fresh-ZIP verification and archive audit are distributed separately
from the immutable ZIP. No current checksum claims to include its own final
checksum. No Lean or independent mathematical review is claimed.
