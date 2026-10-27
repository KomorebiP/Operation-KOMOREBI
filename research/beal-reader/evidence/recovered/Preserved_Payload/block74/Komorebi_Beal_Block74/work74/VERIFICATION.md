# Verification and reproduction

Run python -B verify.py --report ../Block74_Replay.json from the package root.
The report must be outside the immutable package. Default execution checks the
new Block74 finite assertions and integrity, not the complete historical chain.
--replay-predecessor adds only the immediate Block73 default verifier.

The verifier copies this package to a fresh temporary directory, checks the
recorded execution inputs/outputs, DELETES both expected scientific JSONs, and
regenerates them with the primary and separate arithmetic programs. It compares
complete byte hashes after the separate program has independently recalculated
the full certificate. No cached success flag substitutes for execution.

Seven corrupted scientific inputs must be rejected at the exact altered field:
invented actual joint traces, false eight-pattern elimination, erased product
signal, wrong unit count, altered leading coefficient, dropped depth factor,
and a false cyclotomic H1 kernel. An eighth test changes README and requires
rejection by the payload checker. These controlled failures are not failed
scientific runs.

The production programs use the Python standard library, deterministic arithmetic
and no randomness. Each replay command has a90-second wall timeout; an optional
immediate predecessor has180seconds. No operating-system CPU or memory cap is
claimed. The programs themselves are single-threaded.

COMPUTATION_MANIFEST.json is a schema2 execution record with before/after input
hashes, actual commands and runtimes, arithmetic scope, nonclaims, and hashed
results/logs. Explicit PROJECT-LOCAL schema/field/hash checks are performed. No
execution of a separately installed plugin manifest validator is claimed.

The original Block73 default replay completed successfully before the new
development in29.342seconds. Its original JSON and log are retained. The finished
archive gets a fresh-extraction replay and an external checksum/CRC audit, avoiding
a self-referential archive checksum claim.

The finite checks do not prove the local Kummer realization, actual toric
uniformization, global endpoint hypotheses, or any of the eight patterns
impossible. No new Frobenius point counts, Lean, or independent reviewer.
