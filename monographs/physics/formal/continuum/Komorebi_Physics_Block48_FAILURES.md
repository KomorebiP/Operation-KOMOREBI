# Block 48 Failure Ledger

The following attempts were excluded from proof evidence.

1. A direct `lean` invocation outside `lake env` could not resolve the project module prefix.  This was an environment invocation error, not a source error.  The source was recompiled through the attached project environment.
2. Five API, axiom, and negative-control processes were initially launched concurrently.  They contended for the limited memory available and failed to terminate promptly.  They were stopped and rerun sequentially.  Only the completed sequential receipts are accepted.
3. Foreground commands were subject to a short external wrapper window.  Long import-closure builds were run in persistent background sessions and polled until they produced explicit return codes.
4. No timeout, incomplete log, running process, or cache state was treated as a successful verification gate.
