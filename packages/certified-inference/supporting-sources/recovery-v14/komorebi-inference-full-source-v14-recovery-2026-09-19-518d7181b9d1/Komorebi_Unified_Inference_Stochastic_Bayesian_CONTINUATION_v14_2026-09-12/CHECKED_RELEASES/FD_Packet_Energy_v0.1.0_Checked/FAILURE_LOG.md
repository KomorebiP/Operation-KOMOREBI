# Development failures and limitations

Only successful final-source pinned Lean receipts count as checked.

1. The requested streaming execution session for runtime restoration was rejected
   by the container. No Lean process ran in that failed request. Ordinary bounded
   commands restored the runtime, whose part/combined hashes and pinned version
   were checked.
2. The first SelfAdjointPackets draft omitted a decidability instance from a
   theorem signature containing a membership conditional. It also used two
   deprecated conditional-rewrite names. An explicit instance and current names
   fixed the elaboration and warning-as-error failures.
3. The first PacketEnergyDecomposition draft tried to rewrite completeness before
   unfolding its named predicate. Explicitly unfolding the predicate fixed it.
4. One outer tool call checking FDMatrixPacketEnergy was interrupted before a
   completion receipt was written. Its empty log and source snapshot remain.
   It was not counted as a pass. The unchanged module passed when run separately
   with an outer limit larger than the 40-second Lean process cap.
5. The first FDPosteriorPacketFactors draft retained two unused latent-index
   decidability instances in an upper-bound theorem. Those unnecessary section
   variables were omitted. All final sources compile with warnings as errors.

6. The first archive-inventory auditor treated an `end` for a named Lean section
   as a namespace end. That gave two incorrectly shortened parsed theorem names.
   Tracking section and namespace scopes separately fixed the scanner. The Lean
   sources and already successful 165-declaration audit were unchanged.

The final all-declaration axiom audit passed. Two deliberately invalid proof
controls (false equality and placeholder) were rejected as expected. They are
kept under checks, outside active proof sources. They are not release failures.

The installed Mathbox manifest-validator executable was not found in the working
filesystem. The project audit_integrity.py validates final receipts, declarations,
source/output/direct-dependency hashes, complete axiom coverage and diagnostics.
No official Mathbox validator run is claimed.

This block proves mathematical local-upper-bound interfaces. No floating-point
implementation, noise-floor eigensolver or adaptive-termination algorithm has been
verified. No mathematical counterexample to the stated self-adjoint theorem was
found; the oblique example deliberately violates self-adjointness.
