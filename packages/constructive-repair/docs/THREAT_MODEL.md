# Trust boundary and input safety

## What the certificate theorem proves

Lean conclusions concern the literal typed matrices, admissibility rules and costs compiled into the generated input module. A repair satisfies the original equation. A no-repair proof excludes only the original declared class. Minimum-dimensional and minimum-cost repairs are distinct specifications.

## What is not proved

The external JSON parser, Python search, source emitter, command orchestration, hash utilities and filesystem are tested software, not a fully formalized stack. Hashes identify bytes; they are not signatures and do not establish an author's identity. The input echo is a regression/binding check, not a formal proof about the external file parser.

The complete offline kit and imported compiled dependencies are trusted. Pinning a Git revision alone does not independently attest every compiled dependency. The runtime recovered for this audit was matched to the recorded archive hash. Replay uses Lean's own kernel and is not a second independently implemented checker.

## Input controls

External JSON is read through a bounded binary read of at most 4 MiB plus one sentinel byte. A stale file-size observation cannot bypass the limit. The scanner limits structural nesting to 128 and ignores brackets inside quoted strings. Malformed UTF-8, repeated keys, nonfinite values, floats, oversized integer tokens and unexpected schema fields are rejected.

Rational cells use reduced decimal-string numerator and positive denominator pairs, each with at most 512 digits. Matrix dimensions are at most 32 in external records. Branch menus have at most 24 candidates, 4,096 explicitly admitted selections and 8,191 certificate-tree nodes. Internal temporary matrices may be wider than a single serialized input due to column joins.

Matrix objects now require immutable tuple storage. Explicit dimensions cannot silently disagree with values. Boolean row and column indices are rejected even though Python otherwise treats booleans as integer subclasses.

Certificates are bound to a canonical representation of the original problem, not its whitespace. Original inputs and witnesses are emitted separately. Valid rational data cannot contain injected Lean source. The checker, not the certificate producer, derives tree intervals and requires both branches of every split.

## Resource limits are not a sandbox

Exact arithmetic can grow expensive even within shape limits. Search work budgets do not bound every arithmetic instruction or total wall time. Kernel subprocesses have timeouts, but the Python API is not a hardened multi-tenant computation service. Use an externally limited process/container before exposing it to arbitrary public traffic. A stopped or failed computation remains unresolved.

## Evidence handling

Output directories must be new. Partial outputs never supply a successful final receipt before witnesses and checks are complete. The current structured receipt governs the run; a historical PASS elsewhere in the archive is not proof of a fresh execution. A user-supplied JSON object that merely claims success is not a certificate.

The manifest checker detects missing or changed listed files and unsafe manifest paths. It does not establish publication authenticity. Keep a separately trusted archive hash when provenance matters.
