# OSL-Core 0.3 receipt-kernel audit

This is a read-only audit of the `reference/osl_kernel.py` shipped with canonical OSL v0.5. It does not modify or supersede that frozen release.

## Confirmed gaps

1. **A terminal receipt is not required.** The verifier records `program_complete` and `program_reject`, but it never requires exactly one terminal receipt or requires it to be last. The direct probe `KernelVerifier().verify([], {})` returns `all_checks_pass: true`.
2. **Execution is not bound to a live capability grant.** On an `execute` receipt, the kernel verifies the action digest and correspondence with a prior plan, then checks only that `executed` is true and `capability_digest` is nonempty. It does not look up that digest in the capability store or check agent, effect, expiry, revocation, or remaining uses.
3. **Packet construction is not receipt-kind specific.** Observation, communication, inference, and other packet-producing receipts share `_install_packet`. The checker therefore does not establish that observed provenance and observation tokens came only from the observation constructor.
4. **Final-state correspondence is partial and one-way.** Final memories and actions must point back to committed receipts, but reconstructed packets, capabilities, sessions, and all receipt-created objects are not compared bidirectionally with the declared final state.
5. **A bare hash chain has no authenticated anchor.** It detects edits relative to a retained tip, but a party able to replace both the trace and tip can rehash a new internally consistent history. Suffix truncation is also invisible without an expected terminal/source binding or trusted tip.

The packaged v0.5 regression suite still passes. That demonstrates consistency with its encoded tests; it does not discharge the stronger manuscript claims above.

## Highest-leverage next theorem

The next formal release should target receipt-to-semantics refinement:

> For every parsed and well-typed source program, kernel acceptance of an authenticated source binding, terminal receipt sequence, and final state implies a matching typed operational derivation whose receipt projection and final public state are exact; conversely, every valid derivation produces a kernel-accepted trace.

Necessary implementation work includes:

- exactly one final completion or rejection receipt, appearing last
- source-statement and boundary continuity
- receipt-kind-specific packet rules
- observation-token provenance tied to authenticated observation
- proof subject, scope, freshness, and linear-use checks at use time
- complete capability grant lookup, scope matching, expiry, revocation, and use decrement
- bidirectional reconstructed-state equality
- rollback equivalence modulo the append-only audit projection
- an externally authenticated source digest and final chain tip where tamper evidence is claimed

## Relation to the Discovery Bridge

Bridge admission is decided by its own exact finite enumeration and deterministic certificate replay. The OSL-Core adapter is retained to demonstrate source compatibility, but interpreter acceptance is not counted as an independent proof of the bridge's admission result.
